import unittest
from unittest.mock import patch, MagicMock
from src.osw_validator import OSWValidator
from src.models.queue_message_content import Upload
from src.models.queue_message_content import ValidationResult


class TestOSWValidatorService(unittest.TestCase):

    @patch('src.osw_validator.Settings')
    @patch('src.osw_validator.Core')
    def setUp(self, mock_core, mock_settings):
        # Mock Settings
        mock_settings.return_value.event_bus.upload_subscription = 'test_subscription'
        mock_settings.return_value.event_bus.upload_topic = 'test_request_topic'
        mock_settings.return_value.event_bus.validation_topic = 'test_response_topic'
        mock_settings.return_value.max_concurrent_messages = 10
        mock_settings.return_value.get_download_directory.return_value = '/tmp'
        mock_settings.return_value.event_bus.container_name = 'test_container'

        # Mock Core
        mock_core.return_value.get_topic.return_value = MagicMock()
        mock_core.return_value.get_storage_client.return_value = MagicMock()

        # Initialize OSWValidator with mocked dependencies
        self.service = OSWValidator()
        self.service.storage_client = MagicMock()
        self.service.container_name = 'test_container'
        self.service.auth = MagicMock()

        # Define a sample message with proper strings
        self.sample_message = {
            'messageId': 'c8c76e89f30944d2b2abd2491bd95337',  # messageId as string
            'messageType': 'workflow_identifier',  # Ensure this is a string
            'data': {
                'file_upload_path': 'https://tdeisamplestorage.blob.core.windows.net/tdei-storage-test/Archivew.zip',
                'user_id': 'c59d29b6-a063-4249-943f-d320d15ac9ab',
                'tdei_project_group_id': '0b41ebc5-350c-42d3-90af-3af4ad3628fb'
            }
        }

    @patch('src.osw_validator.QueueMessage')
    @patch('src.osw_validator.Upload')
    def test_subscribe_with_valid_message(self, mock_request_message, mock_queue_message):
        # Arrange
        mock_message = MagicMock()
        mock_queue_message.to_dict.return_value = self.sample_message
        mock_request_message.from_dict.return_value = mock_request_message
        self.service.validate = MagicMock()

        # Act
        self.service.start_listening()
        callback = self.service.listening_topic.subscribe.call_args[1]['callback']
        callback(mock_message)

        # Assert
        self.service.validate.assert_called_once_with(received_message=mock_request_message.data_from())

    @patch('src.osw_validator.Validation')
    def test_validate_with_valid_file_path(self, mock_validation):
        # Arrange
        mock_request_message = MagicMock()
        mock_request_message.data.jobId = None
        mock_request_message.data.file_upload_path = 'test_dataset_url'

        # Mock the Validation instance and its return value
        mock_validation_instance = mock_validation.return_value
        result = ValidationResult()
        result.is_valid = True  # Simulate successful validation
        result.validation_message = ''
        mock_validation_instance.validate.return_value = result

        self.service.send_status = MagicMock()

        # Act
        self.service.validate(mock_request_message)

        # Assert
        self.service.send_status.assert_called_once()

        # Extract the actual arguments used in the send_status call
        call_args = self.service.send_status.call_args
        actual_result = call_args[1]['result']
        actual_upload_message = call_args[1]['upload_message']

        # Assert that the properties of the result match what we expect
        self.assertEqual(actual_result.is_valid, result.is_valid)
        self.assertEqual(actual_result.validation_message, result.validation_message)

        # Ensure the upload_message is the expected object
        self.assertEqual(actual_upload_message, mock_request_message)

    @patch('src.osw_validator.ValidationResult')
    def test_validate_with_no_file_upload_path(self, mock_validation_result):
        # Arrange
        mock_request_message = MagicMock()
        mock_request_message.data.file_upload_path = None  # Simulate None file upload path

        # Create the expected failure result
        mock_result = mock_validation_result.return_value
        mock_result.is_valid = False
        mock_result.validation_message = 'Request does not have valid file path specified.'

        self.service.send_status = MagicMock()

        # Act
        self.service.validate(mock_request_message)

        # Assert that send_status was called with failure result
        self.service.send_status.assert_called_once()

        # Extract the actual arguments used in the send_status call
        call_args = self.service.send_status.call_args
        actual_result = call_args[1]['result']
        actual_upload_message = call_args[1]['upload_message']

        # Assert that the result indicates failure
        self.assertFalse(actual_result.is_valid)
        self.assertEqual(actual_result.validation_message,
                         'Error occurred while validating OSW request Request does not have valid file path specified.')

        # Ensure the upload_message is the expected object
        self.assertEqual(actual_upload_message, mock_request_message)

    @patch('src.osw_validator.Validation')
    @patch('src.osw_validator.OSWValidator.has_permission')
    def test_validate_with_validation_only_in_message_type(self, mock_has_permission, mock_validation):
        """Test that has_permission is NOT called when 'VALIDATION_ONLY' is in message_type."""
        # Arrange
        mock_request_message = MagicMock()
        mock_request_message.message_id = 'message_id'

        # Properly mock the 'data' object to avoid AttributeError
        mock_request_message.data = MagicMock()
        mock_request_message.data.file_upload_path = 'test_dataset_url'
        mock_request_message.message_type = 'VALIDATION_ONLY'

        # Ensure has_permission is not called
        mock_has_permission.return_value = None

        # Mock the Validation instance to simulate a successful validation
        mock_validation_instance = mock_validation.return_value
        mock_validation_instance.validate.return_value.is_valid = True
        mock_validation_instance.validate.return_value.validation_message = 'Validation successful'

        # Mock the send_status method
        self.service.send_status = MagicMock()

        # Act
        self.service.validate(mock_request_message)

        # Assert
        # Ensure has_permission was NOT called since VALIDATION_ONLY is in the message_type
        mock_has_permission.assert_not_called()

        # Ensure send_status was called with a successful validation result
        self.service.send_status.assert_called_once()

        # Extract the actual result and upload message
        actual_result = self.service.send_status.call_args[1]['result']
        actual_upload_message = self.service.send_status.call_args[1]['upload_message']

        # Assert the result is valid and the upload_message is the mock_request_message
        self.assertTrue(actual_result.is_valid)
        self.assertEqual(actual_upload_message, mock_request_message)

    @patch('src.osw_validator.threading.Thread')
    def test_stop_listening(self, mock_thread):
        # Arrange
        mock_thread_instance = MagicMock()
        mock_thread.return_value = mock_thread_instance

        self.service.listener_thread = mock_thread_instance

        # Act
        result = self.service.stop_listening()

        # Assert
        mock_thread_instance.join.assert_called_once_with(timeout=0)
        self.assertIsNone(result)

    def test_has_permission_success(self):
        mock_message = Upload(data={
            'data': {
                'user_id': '1233',
                'tdei_project_group_id': '444444'
            },
            'message': 'test_message',
            'messageType': 'message_type',
            'messageId': '123'
        })

        self.service.auth.has_permission = MagicMock()
        self.service.auth.has_permission.return_value = True

        result = self.service.has_permission(
            roles=['tdei-admin', 'poc', 'osw_data_generator'],
            queue_message=mock_message
        )
        self.assertTrue(result)
        self.service.auth.has_permission.assert_called_once()

    def test_has_permission_failure(self):
        mock_message = Upload(data={
            'data': {
                'user_id': '1233',
                'tdei_project_group_id': '444444'
            },
            'message': 'test_message',
            'messageType': 'message_type',
            'messageId': '123'
        })

        self.service.auth.has_permission = MagicMock()
        self.service.auth.has_permission.return_value = False

        result = self.service.has_permission(
            roles=[],
            queue_message=mock_message
        )
        self.assertFalse(result)
        self.service.auth.has_permission.assert_called_once()

    def test_has_permission_exception(self):
        mock_message = Upload(data={
            'data': {
                'user_id': '1233',
                'tdei_project_group_id': '444444'
            },
            'message': 'test_message',
            'messageType': 'message_type',
            'messageId': '123'
        })

        self.service.auth.has_permission = MagicMock()
        self.service.auth.has_permission.side_effect = Exception('Mock exception')

        result = self.service.has_permission(
            roles=[],
            queue_message=mock_message
        )
        self.assertFalse(result)
        self.service.auth.has_permission.assert_called_once()

    def test_send_status_success(self):
        validation_result = ValidationResult()
        validation_result.is_valid = True
        validation_result.validation_message = ''

        mock_message = Upload(data={
            'data': {
                'user_id': '1233',
                'tdei_project_group_id': '444444'
            },
            'message': 'test_message',
            'messageType': 'message_type',
            'messageId': '123'
        })

        mock_topic = self.service.core.get_topic.return_value
        mock_publish = mock_topic.publish

        self.service.send_status(result=validation_result, upload_message=mock_message)

        mock_publish.assert_called_once()

    def test_send_status_failure(self):
        validation_result = ValidationResult()
        validation_result.is_valid = False
        validation_result.validation_message = 'Failed'

        mock_message = Upload(data={
            'data': {
                'user_id': '1233',
                'tdei_project_group_id': '444444'
            },
            'message': 'test_message',
            'messageType': 'message_type',
            'messageId': '123'
        })

        mock_topic = self.service.core.get_topic.return_value
        mock_publish = mock_topic.publish

        self.service.send_status(result=validation_result, upload_message=mock_message)

        mock_publish.assert_called_once()

    def test_send_status_exception(self):
        validation_result = ValidationResult()
        validation_result.is_valid = False
        validation_result.validation_message = 'Failed'

        mock_message = Upload(data={
            'data': {
                'user_id': '1233',
                'tdei_project_group_id': '444444'
            },
            'message': 'test_message',
            'messageType': 'message_type',
            'messageId': '123'
        })

        mock_topic = self.service.core.get_topic.return_value
        mock_publish = mock_topic.publish
        mock_publish.side_effect = Exception('Mock Exception')

        self.service.send_status(result=validation_result, upload_message=mock_message)

        mock_publish.assert_called_once()

    def test_validate_with_unauthorized(self):
        # Arrange
        self.service.has_permission = MagicMock()
        self.service.has_permission.return_value = None

        mock_message = Upload(data={
            'data': {
                'user_id': '1233',
                'tdei_project_group_id': '444444',
                'file_upload_path': 'mock_file_upload_path'
            },
            'message': 'test_message',
            'messageType': 'message_type',
            'messageId': '123'
        })

        # Mock the send_status method
        self.service.send_status = MagicMock()

        # Act
        self.service.validate(mock_message)

        # Assert

        # Ensure send_status was called with a successful validation result
        self.service.send_status.assert_called_once()

        # Extract the actual result and upload message
        actual_result = self.service.send_status.call_args[1]['result']
        actual_upload_message = self.service.send_status.call_args[1]['upload_message']

        # Assert the result is valid and the upload_message is the mock_request_message
        self.assertFalse(actual_result.is_valid)
        self.service.has_permission.assert_called_once()


if __name__ == '__main__':
    unittest.main()
