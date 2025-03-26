import os
import unittest
from unittest.mock import patch, Mock, mock_open
import sys
import tempfile
import io

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from api_interface import interact_with_gemini_api

class TestApiInterface(unittest.TestCase):
    def setUp(self):
        # Set up API key for tests
        os.environ['GEMINI_API_KEY'] = 'test_api_key'
        
        # Mock API responses
        self.mock_text_response = {'response': 'This is a text response'}
        self.mock_file_response = {'response': 'This is a file response'}
    
    def tearDown(self):
        # Clean up environment after tests
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
    
    @patch('api_interface.GeminiAPI')
    def test_interact_with_gemini_api_text_prompt(self, mock_gemini_api_class):
        # Set up the mock
        mock_gemini_api = Mock()
        mock_gemini_api_class.return_value = mock_gemini_api
        mock_gemini_api.send_text_prompt.return_value = self.mock_text_response
        
        # Call function with a text prompt
        result = interact_with_gemini_api(
            prompt="What is the capital of France?",
            file_path=None,
            folder_path=None,
            output_type='text',
            model_name='gemini-pro'
        )
        
        # Verify GeminiAPI was instantiated with the correct API key
        mock_gemini_api_class.assert_called_once_with('test_api_key')
        
        # Verify send_text_prompt was called with the correct arguments
        mock_gemini_api.send_text_prompt.assert_called_once_with(
            "What is the capital of France?", 
            model='gemini-pro'
        )
        
        # Verify the function returns the expected result
        self.assertEqual(result, 'This is a text response')
    
    @patch('api_interface.GeminiAPI')
    @patch('api_interface.validate_file_path')
    def test_interact_with_gemini_api_file_prompt(self, mock_validate_file, mock_gemini_api_class):
        # Set up the mocks
        mock_gemini_api = Mock()
        mock_gemini_api_class.return_value = mock_gemini_api
        mock_gemini_api.send_file_prompt.return_value = self.mock_file_response
        
        # Call function with a file path
        result = interact_with_gemini_api(
            prompt=None,
            file_path="test_file.txt",
            folder_path=None,
            output_type='text',
            model_name='gemini-pro'
        )
        
        # Verify file path was validated
        mock_validate_file.assert_called_once_with("test_file.txt")
        
        # Verify send_file_prompt was called with the correct arguments
        mock_gemini_api.send_file_prompt.assert_called_once_with(
            "test_file.txt", 
            model='gemini-pro'
        )
        
        # Verify the function returns the expected result
        self.assertEqual(result, 'This is a file response')
    
    @patch('api_interface.GeminiAPI')
    @patch('api_interface.validate_folder_path')
    def test_interact_with_gemini_api_with_folder_context(self, mock_validate_folder, mock_gemini_api_class):
        # Set up the mocks
        mock_gemini_api = Mock()
        mock_gemini_api_class.return_value = mock_gemini_api
        mock_gemini_api.send_text_prompt.return_value = self.mock_text_response
        
        # Call function with folder context
        result = interact_with_gemini_api(
            prompt="What is the capital of France?",
            file_path=None,
            folder_path="test_folder",
            output_type='text',
            model_name='gemini-pro'
        )
        
        # Verify folder path was validated
        mock_validate_folder.assert_called_once_with("test_folder")
        
        # Verify send_text_prompt was called with folder context included
        mock_gemini_api.send_text_prompt.assert_called_once()
        args, kwargs = mock_gemini_api.send_text_prompt.call_args
        self.assertIn("Using context from folder: test_folder", args[0])
        self.assertIn("What is the capital of France?", args[0])
        
        # Verify the function returns the expected result
        self.assertEqual(result, 'This is a text response')
    
    @patch('PIL.Image.open')
    @patch('api_interface.process_image')
    @patch('api_interface.validate_file_path')
    def test_interact_with_gemini_api_image_output(self, mock_validate_file, mock_process_image, mock_image_open):
        # Set up image processing mock
        mock_processed_image = Mock()
        mock_process_image.return_value = mock_processed_image
        mock_image_open.return_value = mock_processed_image

        # Call function with image output type
        result = interact_with_gemini_api(
            prompt="Generate an image of a cat",
            file_path="cat.jpg",
            folder_path=None,
            output_type='image',
            model_name='gemini-pro-vision'
        )

        # Verify file path was validated
        mock_validate_file.assert_called_once_with("cat.jpg")

        # Verify image was processed
        mock_process_image.assert_called_once_with("cat.jpg")

        # Verify binary data is returned for image output
        self.assertIsInstance(result, bytes)
    
    def test_interact_with_gemini_api_missing_api_key(self):
        # Remove API key from environment
        if 'GEMINI_API_KEY' in os.environ:
            del os.environ['GEMINI_API_KEY']
        
        # Test that an exception is raised when API key is missing
        with self.assertRaises(EnvironmentError) as context:
            interact_with_gemini_api(
                prompt="Test prompt",
                file_path=None,
                folder_path=None,
                output_type='text',
                model_name='gemini-pro'
            )
        
        # Check exception message
        self.assertIn("GEMINI_API_KEY environment variable is not set", str(context.exception))
    
    def test_interact_with_gemini_api_no_input(self):
        # Test that an exception is raised when neither prompt nor file is provided
        with self.assertRaises(ValueError) as context:
            interact_with_gemini_api(
                prompt=None,
                file_path=None,
                folder_path=None,
                output_type='text',
                model_name='gemini-pro'
            )
        
        # Check exception message
        self.assertEqual("Either a prompt or file path must be provided.", str(context.exception))

if __name__ == "__main__":
    unittest.main()