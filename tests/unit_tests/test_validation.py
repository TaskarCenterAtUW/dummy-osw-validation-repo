import os
import json
import unittest
from pathlib import Path
from src.validation import Validation
from unittest.mock import patch, MagicMock

DOWNLOAD_FILE_PATH = f'{Path.cwd()}/downloads'
SAVED_FILE_PATH = f'{Path.cwd()}/tests/unit_tests/test_files'

SUCCESS_FILE_NAME = 'valid.zip'
FAILURE_FILE_NAME = 'invalid.zip'
ID_MISSING_FILE_NAME = '_id_missing.zip'
EDGES_INVALID_FILE_NAME = 'edges_invalid.zip'
NODES_INVALID_FILE_NAME = 'nodes_invalid.zip'
POINTS_INVALID_FILE_NAME = 'points_invalid.zip'
INVALID_FILE_NAME = 'invalid_files.zip'
INVALID_GEOMETRY_FILE_NAME = 'invalid_geometry.zip'
MISSING_IDENTIFIER_FILE_NAME = 'missing_identifier.zip'
NO_ENTITY_FILE_NAME = 'no_entity.zip'
WRONG_DATATYPE_FILE_NAME = 'wrong_datatype.zip'


class TestValidation(unittest.TestCase):

    @patch('src.validation.Settings')
    def setUp(self, mock_settings):
        # Mock Settings and storage client to avoid actual dependencies
        mock_settings.return_value.event_bus.container_name = 'test_container'

        self.mock_storage_client = MagicMock()

        # Test-specific setup
        self.file_path = '/path/to/test.zip'
        self.validation = Validation(file_path=self.file_path, storage_client=self.mock_storage_client)

    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    @patch('src.validation.uuid.uuid1')
    def test_validation_init_creates_unique_dir(self, mock_uuid, mock_exists, mock_makedirs):
        """Test that the Validation class correctly creates directories."""
        mock_uuid.return_value.hex = 'fixeduuidhex'
        unique_id = 'fixeduuidhex'[0:24]
        expected_dir = os.path.join(Path.cwd(), 'downloads', unique_id)

        # Act by reinitializing to trigger the directory creation
        self.validation = Validation(file_path=self.file_path, storage_client=self.mock_storage_client)

        # Assert that os.makedirs was called for the unique dir path
        mock_makedirs.assert_called_with(expected_dir)

    @patch('src.validation.Validation.clean_up')
    @patch('src.validation.Validation.download_single_file')
    def test_validate_valid_zip(self, mock_download_file, mock_clean_up):
        """Test the validate method for a valid zip file."""

        mock_download_file.return_value = f'{SAVED_FILE_PATH}/{SUCCESS_FILE_NAME}'
        # Act
        result = self.validation.validate(max_errors=10)

        # Assert that validation is marked as valid
        self.assertTrue(result.is_valid)
        self.assertEqual(result.validation_message, '')

        # Ensure clean_up is called twice (once for the file, once for the folder)
        self.assertEqual(mock_clean_up.call_count, 2)


    @patch('src.validation.Validation.clean_up')
    @patch('src.validation.Validation.download_single_file')
    def test_validate_invalid_file(self, mock_download_file, mock_clean_up):
        """Test the validate method for a invalid file."""
        mock_download_file.return_value = f'{SAVED_FILE_PATH}/{FAILURE_FILE_NAME}'
        # Act
        result = self.validation.validate(max_errors=10)

        # Assert that validation is marked as valid
        self.assertFalse(result.is_valid)
        errors = json.loads(result.validation_message)
        self.assertNotEqual(len(errors), 0)


        # Ensure clean_up is called twice (once for the file, once for the folder)
        self.assertEqual(mock_clean_up.call_count, 2)

    @patch('src.validation.Validation.clean_up')
    @patch('src.validation.Validation.download_single_file')
    def test_validate_invalid_file_with_errors(self, mock_download_file, mock_clean_up):
        """Test the validate method for a invalid file."""
        mock_download_file.return_value = f'{SAVED_FILE_PATH}/{FAILURE_FILE_NAME}'
        error_in_file = 'wa.microsoft.graph.edges.OSW.geojson'
        expected_errors = [
            {
                'feature_index': 3,
                'error_message': "Additional properties are not allowed ('crossing' was unexpected). If you want to carry this tag, change it to ext:crossing"
            },
            {
                'feature_index': 6,
                'error_message': "Additional properties are not allowed ('crossing' was unexpected). If you want to carry this tag, change it to ext:crossing"
            },
            {
                'feature_index': 8,
                'error_message': "Additional properties are not allowed ('crossing' was unexpected). If you want to carry this tag, change it to ext:crossing"
            },
            {
                'feature_index': 25,
                'error_message': "Additional properties are not allowed ('crossing' was unexpected). If you want to carry this tag, change it to ext:crossing"
            },
            {
                'feature_index': 27,
                'error_message': "Additional properties are not allowed ('crossing' was unexpected). If you want to carry this tag, change it to ext:crossing"
            }
        ]
        # Act
        result = self.validation.validate(max_errors=10)

        # Assert that validation is marked as valid
        self.assertFalse(result.is_valid)
        errors = json.loads(result.validation_message)
        self.assertEqual(len(errors), len(expected_errors))

        for expected, error in zip(expected_errors, errors):
            self.assertEqual(error['filename'], error_in_file)
            self.assertEqual(error['feature_index'], expected['feature_index'])
            self.assertEqual(error['error_message'][0], expected['error_message'])
        # Ensure clean_up is called twice (once for the file, once for the folder)
        self.assertEqual(mock_clean_up.call_count, 2)

    @patch('src.validation.OSWValidation')
    @patch('src.validation.Validation.clean_up')
    def test_validate_invalid_zip(self, mock_clean_up, mock_osw_validation):
        """Test validate method for invalid zip file with errors."""
        # Mock the OSWValidation validate method to return errors
        mock_validation_result = MagicMock()
        mock_validation_result.is_valid = False
        mock_validation_result.errors = 'Failed to validate because unknown file format'
        mock_osw_validation.return_value.validate.return_value = mock_validation_result

        # Act
        result = self.validation.validate(max_errors=10)

        # Assert that validation failed and the error message is returned
        self.assertFalse(result.is_valid)
        self.assertEqual(result.validation_message, 'Failed to validate because unknown file format')

        # Ensure clean_up is called twice (once for the file, once for the folder)
        self.assertEqual(mock_clean_up.call_count, 1)

    @patch('src.validation.Validation.download_single_file')
    def test_validate_unknown_file_format(self, mock_download_file):
        """Test validation failure for unknown file format."""

        # Mock the file path with a non-zip extension to trigger the else block
        self.validation.file_relative_path = 'invalid_file.txt'

        # Mock download to not affect the actual download method
        mock_download_file.return_value = '/path/to/invalid_file.txt'

        # Act
        result = self.validation.validate(max_errors=10)

        # Assert that the validation failed due to unknown file format
        self.assertFalse(result.is_valid)
        self.assertEqual(result.validation_message, 'Failed to validate because unknown file format')

    @patch('src.validation.Validation.download_single_file', return_value=f'{SAVED_FILE_PATH}/{SUCCESS_FILE_NAME}')
    @patch('gc.collect')
    @patch('shutil.rmtree')
    @patch('os.remove')
    def test_gc_collect_called(self, mock_remove, mock_rmtree, mock_gc, mock_download_file):
        """Test if garbage collection is called."""
        # Mock the storage client to return a bytes-like stream
        file_mock = MagicMock()
        file_mock.get_stream.return_value = b'file content'

        # Replace self.validation.storage_client.get_file_from_url to return the mocked file object
        self.validation.storage_client.get_file_from_url.return_value = file_mock

        # Simulate validation process
        self.validation.validate(max_errors=10)

        # Ensure garbage collection is called
        mock_gc.assert_called()

        # Ensure cleanup methods are called for valid paths
        mock_remove.assert_called_once_with(f'{SAVED_FILE_PATH}/{SUCCESS_FILE_NAME}')

    @patch('os.remove')
    @patch('os.path.isfile', return_value=True)
    def test_clean_up_file(self, mock_isfile, mock_remove):
        """Test the static clean_up method with a file path."""
        # Act
        Validation.clean_up('/path/to/file.zip')

        # Assert that os.remove is called for a file
        mock_remove.assert_called_once_with('/path/to/file.zip')

    @patch('os.remove')
    @patch('shutil.rmtree')
    def test_clean_up_directory(self, mock_rmtree, mock_remove):
        """Test the static clean_up method with a directory path."""
        # Act
        Validation.clean_up('/path/to/directory')

        # Assert that shutil.rmtree is called for a directory
        mock_rmtree.assert_called_once_with('/path/to/directory', ignore_errors=False)
        mock_remove.assert_not_called()

    @patch('src.validation.uuid.uuid1')
    def test_get_unique_id(self, mock_uuid):
        """Test get_unique_id to ensure correct ID generation."""
        # Arrange
        mock_uuid.return_value.hex = 'mockuuidhex'

        # Act
        unique_id = self.validation.get_unique_id()

        # Assert that the unique ID is generated as expected
        self.assertEqual(unique_id, 'mockuuidhex'[0:24])


if __name__ == '__main__':
    unittest.main()
