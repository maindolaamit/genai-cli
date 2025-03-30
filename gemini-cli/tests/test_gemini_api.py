import os
import unittest
from unittest.mock import patch, Mock, mock_open
import json
import sys
import tempfile

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from gemini_api import GeminiAPI

class TestGeminiAPI(unittest.TestCase):
    def setUp(self):
        # Set up a test API key and API instance
        self.api_key = "test_api_key"
        self.gemini_api = GeminiAPI(self.api_key)

        # Mock response for successful API calls
        self.mock_successful_response = Mock()
        self.mock_successful_response.text = "This is a test response from Gemini API"

        # Mock response for failed API calls (not directly used in google-genai, but keep for error test)
        self.mock_failed_response = Mock()
        self.mock_failed_response.status_code = 400
        self.mock_failed_response.text = "Bad Request" # Not used with google-genai

    @patch('google.generativeai.GenerativeModel')
    def test_send_text_prompt_success(self, mock_generative_model):
        # Mock the API response
        mock_response_obj = Mock()
        mock_response_obj.text = "This is a test response from Gemini API"
        mock_generative_model.return_value.generate_content_and_save.return_value = mock_response_obj

        # Send a text prompt
        response = self.gemini_api.send_text_prompt("What is the capital of France?")

        # Verify the request was properly formatted
        mock_generative_model.assert_called_once_with('gemini-pro')
        mock_generative_model.return_value.generate_content_and_save.assert_called_once_with("What is the capital of France?")

        # Verify response
        self.assertEqual(response, {"response": "This is a test response from Gemini API", 'model': 'gemini-pro'})

    @patch('google.generativeai.GenerativeModel')
    def test_send_text_prompt_failure(self, mock_generative_model):
        # Mock a failed API response
        mock_generative_model.return_value.generate_content_and_save.side_effect = Exception("API Error")

        # Test that an exception is raised for a failed request
        with self.assertRaises(Exception) as context:
            self.gemini_api.send_text_prompt("Invalid prompt")

        # Check exception message
        self.assertTrue("Error sending text prompt to Gemini API: API Error" in str(context.exception))

    @patch('PIL.Image.open')
    @patch('google.genai.Model')
    def test_send_file_prompt_success(self, mock_generative_model, mock_image_open):
        # Mock the API response
        mock_response_obj = Mock()
        mock_response_obj.text = "This is a test response from Gemini API"
        mock_generative_model.return_value.generate.return_value = mock_response_obj
        mock_image_open.return_value = Mock()

        # Create a test file and mock the open function
        test_file_content = "Test file content"
        test_file_path = "test_file.txt"

        # Use patch to mock open and Image.open
        with patch("builtins.open", mock_open(read_data=test_file_content)):
            response = self.gemini_api.send_file_prompt(test_file_path)

            # Verify the request was properly formatted
            mock_generative_model.assert_called_once_with('gemini-pro-vision')
            mock_generative_model.return_value.generate.assert_called_once()  # Called with image

            # Verify response
            self.assertEqual(response, {"response": "This is a test response from Gemini API", 'model': 'gemini-pro-vision'})

    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_output(self, mock_json_dump, mock_file):
        # Test output data
        output_data = {"key": "value"}
        output_path = "output.json"

        # Save the output
        self.gemini_api.save_output(output_data, output_path)

        # Verify file was opened with write permissions
        mock_file.assert_called_once_with(output_path, 'w')

        # Verify json.dump was called with the right arguments
        mock_json_dump.assert_called_once()
        args, kwargs = mock_json_dump.call_args
        self.assertEqual(args[0], output_data)  # First arg should be the data
        self.assertEqual(args[1], mock_file())  # Second arg should be the file handle

    def test_get_default_models(self):
        # Test retrieving default models
        models = self.gemini_api.get_default_models()
        self.assertEqual(models, ['gemini-pro', 'gemini-pro-vision', 'gemini-1.5-pro'])

if __name__ == "__main__":
    unittest.main()