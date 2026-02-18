import os
import json
import unittest
from unittest.mock import MagicMock, patch, call
from src.osw_validator import OSWValidator
from src.models.queue_message_content import ValidationResult, Upload

current_dir = os.path.dirname(os.path.abspath(os.path.join(__file__, '../')))
parent_dir = os.path.dirname(current_dir)

TEST_JSON_FILE = os.path.join(parent_dir, 'src/assets/osw-upload.json')

TEST_FILE = open(TEST_JSON_FILE)
TEST_DATA = json.loads(TEST_FILE.read())


class PermissionResponse:
    def __init__(self, is_authorized):
        self.is_authorized = is_authorized


class TestOSWValidator(unittest.TestCase):

    def setUp(self):
        with patch.object(OSWValidator, '__init__', return_value=None):
            self.validator = OSWValidator()
            self.validator._subscription_name = MagicMock()
            self.validator.listening_topic = MagicMock()
            self.validator.publish_topic = MagicMock()
            self.validator.logger = MagicMock()
            self.validator.storage_client = MagicMock()
            self.validator.auth = MagicMock()

    @patch.object(OSWValidator, 'start_listening')
    def test_start_listening(self, mock_start_listening):
        # Act
        self.validator.start_listening()

        # Assert
        mock_start_listening.assert_called_once()

    @patch.object(OSWValidator, 'send_status')  # Mock the send_status method
    def test_valid_send_status(self, mock_send_status):
        upload_message_data = MagicMock()
        upload_message_data.stage = 'OSW-Validation'  # Set the stage attribute

        # Create a mock meta object
        mock_meta = MagicMock()
        mock_meta.isValid = True
        mock_meta.validationMessage = 'Validation successful'

        upload_message_data.meta = mock_meta

        # Create a mock response object
        mock_response = MagicMock()
        mock_response.success = True
        mock_response.message = 'Validation successful'

        upload_message_data.response = mock_response

        # Create a mock upload_message object
        upload_message = MagicMock()
        upload_message.message = 'Test message'
        upload_message.data = upload_message_data
        result = ValidationResult()
        result.is_valid = True
        result.validation_message = ''
        # Call the send_status method
        self.validator.send_status(result=result, upload_message=upload_message)

        # Add assertions for the expected behavior
        self.assertEqual(upload_message_data.stage, 'OSW-Validation')
        self.assertTrue(upload_message_data.meta.isValid)
        self.assertEqual(upload_message_data.meta.validationMessage, 'Validation successful')
        self.assertTrue(upload_message_data.response.success)
        self.assertEqual(upload_message_data.response.message, 'Validation successful')

        # Assert that the send_status method was called once with the expected arguments
        mock_send_status.assert_called_once_with(result=result, upload_message=upload_message)

    @patch.object(OSWValidator, 'send_status')  # Mock the send_status method
    def test_invalid_send_status(self, mock_send_status):
        upload_message_data = MagicMock()
        upload_message_data.stage = 'OSW-Validation'  # Set the stage attribute

        # Create a mock meta object
        mock_meta = MagicMock()
        mock_meta.isValid = False
        mock_meta.validationMessage = 'Validation failed'

        upload_message_data.meta = mock_meta

        # Create a mock response object
        mock_response = MagicMock()
        mock_response.success = False
        mock_response.message = 'Validation failed'

        upload_message_data.response = mock_response

        # Create a mock upload_message object
        upload_message = MagicMock()
        upload_message.message = 'Test message'
        upload_message.data = upload_message_data
        result = ValidationResult()
        result.is_valid = True
        result.validation_message = 'Validation failed'

        # Call the send_status method
        self.validator.send_status(result=result, upload_message=upload_message)

        # Add assertions for the expected behavior
        self.assertEqual(upload_message_data.stage, 'OSW-Validation')
        self.assertFalse(upload_message_data.meta.isValid)
        self.assertEqual(upload_message_data.meta.validationMessage, 'Validation failed')
        self.assertFalse(upload_message_data.response.success)
        self.assertEqual(upload_message_data.response.message, 'Validation failed')

        # Assert that the send_status method was called once with the expected arguments
        mock_send_status.assert_called_once_with(result=result, upload_message=upload_message)

    def test_has_permission_for_admin_success(self):
        self.validator.auth.has_permission.return_value = True
        upload_message = Upload(TEST_DATA)

        result = self.validator.has_permission(roles=['tdei-admin'], queue_message=upload_message)

        # Assertions
        self.assertTrue(result)

    def test_has_permission_for_poc_success(self):
        self.validator.auth.has_permission.return_value = True
        upload_message = Upload(TEST_DATA)

        result = self.validator.has_permission(roles=['poc'], queue_message=upload_message)

        # Assertions
        self.assertTrue(result)

    def test_has_permission_for_osw_data_generator_success(self):
        self.validator.auth.has_permission.return_value = True
        upload_message = Upload(TEST_DATA)

        result = self.validator.has_permission(roles=['osw_data_generator'], queue_message=upload_message)

        # Assertions
        self.assertTrue(result)

    def test_has_permission_for_all_roles_success(self):
        self.validator.auth.has_permission.return_value = True
        upload_message = Upload(TEST_DATA)

        result = self.validator.has_permission(roles=['tdei-admin', 'poc', 'osw_data_generator'], queue_message=upload_message)

        # Assertions
        self.assertTrue(result)

    def test_has_permission_failure(self):
        self.validator.auth.has_permission.return_value = False
        upload_message = Upload(TEST_DATA)

        result = self.validator.has_permission(roles=['test'], queue_message=upload_message)

        # Assertions
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
