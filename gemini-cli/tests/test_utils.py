import os
import unittest
from unittest.mock import patch, mock_open
import sys
import tempfile
from PIL import Image
import io

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from utils import read_file, validate_file_path, validate_folder_path, load_environment_variable, process_image

class TestUtils(unittest.TestCase):
    def test_read_file(self):
        # Test reading a file with mock_open
        mock_file_content = "Test file content"
        with patch("builtins.open", mock_open(read_data=mock_file_content)):
            content = read_file("dummy_path.txt")
            self.assertEqual(content, mock_file_content)
    
    def test_validate_file_path_valid(self):
        # Create a temporary file and test validation
        with tempfile.NamedTemporaryFile() as temp_file:
            try:
                validate_file_path(temp_file.name)
            except FileNotFoundError:
                self.fail("validate_file_path raised FileNotFoundError unexpectedly!")
    
    def test_validate_file_path_invalid(self):
        # Test with a non-existent file path
        with self.assertRaises(FileNotFoundError):
            validate_file_path("/path/to/nonexistent/file.txt")
    
    def test_validate_folder_path_valid(self):
        # Create a temporary directory and test validation
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                validate_folder_path(temp_dir)
            except NotADirectoryError:
                self.fail("validate_folder_path raised NotADirectoryError unexpectedly!")
    
    def test_validate_folder_path_invalid(self):
        # Test with a non-existent directory path
        with self.assertRaises(NotADirectoryError):
            validate_folder_path("/path/to/nonexistent/directory/")
    
    def test_load_environment_variable_exists(self):
        # Set an environment variable and test loading it
        test_var_name = "TEST_ENVIRONMENT_VARIABLE"
        test_var_value = "test_value"
        with patch.dict(os.environ, {test_var_name: test_var_value}):
            value = load_environment_variable(test_var_name)
            self.assertEqual(value, test_var_value)
    
    def test_load_environment_variable_missing(self):
        # Test loading a non-existent environment variable
        with patch.dict(os.environ, clear=True):
            with self.assertRaises(EnvironmentError):
                load_environment_variable("NONEXISTENT_VARIABLE")
    
    def test_process_image(self):
        # Create a test image
        test_image = Image.new('RGB', (512, 512), color='red')
        test_image_path = "test_image.jpg"
        
        # Mock open to return our test image
        with patch('PIL.Image.open') as mock_image_open:
            mock_image_open.return_value = test_image
            
            # Process the image
            processed_image = process_image(test_image_path)
            
            # Check the size of processed image
            self.assertEqual(processed_image.size, (256, 256))

if __name__ == "__main__":
    unittest.main()