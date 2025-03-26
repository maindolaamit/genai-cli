import os
import unittest
from unittest.mock import patch, Mock, mock_open
import sys
import tempfile
import argparse
import io

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

# Import the module we want to test, using patch to avoid executing main()
with patch('argparse.ArgumentParser.parse_args'):
    import cli

class TestCLI(unittest.TestCase):
    
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('argparse.ArgumentParser.parse_args')
    @patch('cli.interact_with_gemini_api')
    def test_main_with_prompt_only(self, mock_interact, mock_args, mock_stdout):
        # Mock the argument parser
        mock_args.return_value = Mock(
            prompt="Test prompt",
            file=None,
            folder=None, 
            output=None,
            output_type='text',
            model=None
        )
        
        # Mock the API interaction
        mock_interact.return_value = "API response"
        
        # Call the main function
        cli.main()
        
        # Verify that interact_with_gemini_api was called with correct arguments
        mock_interact.assert_called_once_with(
            "Test prompt", None, None, 'text', cli.MODEL_MAP[cli.DEFAULT_TEXT_MODEL]
        )
    
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('argparse.ArgumentParser.parse_args')
    @patch('cli.interact_with_gemini_api')
    @patch('os.path.isfile')
    def test_main_with_file(self, mock_isfile, mock_interact, mock_args, mock_stdout):
        # Set up mocks
        test_file_path = "/path/to/file.txt"
        mock_isfile.return_value = True
        
        # Mock the argument parser
        mock_args.return_value = Mock(
            prompt=None,
            file=test_file_path,
            folder=None, 
            output=None,
            output_type='text',
            model=None
        )
        
        # Mock the API interaction
        mock_interact.return_value = "API response"
        
        # Call the main function
        cli.main()
        
        # Verify that interact_with_gemini_api was called with correct arguments
        mock_interact.assert_called_once_with(
            None, test_file_path, None, 'text', cli.MODEL_MAP[cli.DEFAULT_TEXT_MODEL]
        )
    
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('argparse.ArgumentParser.parse_args')
    @patch('cli.interact_with_gemini_api')
    @patch('os.path.isdir')
    @patch('os.path.isfile')
    def test_main_with_prompt_and_output(self, mock_isfile, mock_isdir, mock_interact, mock_args, mock_stdout):
        # Set up mocks
        test_output_path = "/path/to/output.txt"
        mock_isfile.return_value = False
        mock_isdir.return_value = True
        
        # Mock the argument parser
        mock_args.return_value = Mock(
            prompt="Test prompt",
            file=None,
            folder="/path/to/folder", 
            output=test_output_path,
            output_type='text',
            model=None
        )
        
        # Mock the API interaction and file writing
        mock_interact.return_value = "API response"
        mock_file = mock_open()
        
        # Call the main function with mocked file open
        with patch('builtins.open', mock_file):
            cli.main()
        
        # Verify that interact_with_gemini_api was called with correct arguments
        mock_interact.assert_called_once_with(
            "Test prompt", None, "/path/to/folder", 'text', cli.MODEL_MAP[cli.DEFAULT_TEXT_MODEL]
        )
        
        # Verify that the file was opened and written to
        mock_file.assert_called_once_with(test_output_path, 'w')
        mock_file().write.assert_called_once_with("API response")
    
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('argparse.ArgumentParser.parse_args')
    @patch('cli.interact_with_gemini_api')
    def test_model_selection_with_custom_model(self, mock_interact, mock_args, mock_stdout):
        # Mock the argument parser with a custom model
        mock_args.return_value = Mock(
            prompt="Test prompt",
            file=None,
            folder=None, 
            output=None,
            output_type='text',
            model="adv-txt"
        )
        
        # Mock the API interaction
        mock_interact.return_value = "API response"
        
        # Call the main function
        cli.main()
        
        # Verify that interact_with_gemini_api was called with the correct model
        mock_interact.assert_called_once_with(
            "Test prompt", None, None, 'text', cli.MODEL_MAP["adv-txt"]
        )
    
    @patch('sys.stdout', new_callable=io.StringIO)
    @patch('argparse.ArgumentParser.parse_args')
    @patch('cli.interact_with_gemini_api')
    def test_model_selection_with_unknown_model(self, mock_interact, mock_args, mock_stdout):
        # Mock the argument parser with an unknown model
        mock_args.return_value = Mock(
            prompt="Test prompt",
            file=None,
            folder=None, 
            output=None,
            output_type='text',
            model="unknown-model"
        )
        
        # Mock the API interaction
        mock_interact.return_value = "API response"
        
        # Call the main function
        cli.main()
        
        # Verify that interact_with_gemini_api was called with the default model
        # and that a warning was printed
        mock_interact.assert_called_once_with(
            "Test prompt", None, None, 'text', cli.MODEL_MAP[cli.DEFAULT_TEXT_MODEL]
        )
        self.assertIn("Warning: Model code 'unknown-model' not recognized", mock_stdout.getvalue())
    
    @patch('sys.stderr', new_callable=io.StringIO)
    @patch('argparse.ArgumentParser.parse_args')
    @patch('argparse.ArgumentParser.error')
    def test_main_with_no_prompt_or_file(self, mock_error, mock_args, mock_stderr):
        # Mock the argument parser with no prompt or file
        mock_args.return_value = Mock(
            prompt=None,
            file=None,
            folder=None, 
            output=None,
            output_type='text',
            model=None
        )
        
        # Mock the parser error method
        mock_error.side_effect = SystemExit
        
        # Call the main function and expect a system exit
        with self.assertRaises(SystemExit):
            cli.main()
        
        # Verify that the parser error method was called with the correct message
        mock_error.assert_called_once_with('At least one of --prompt or --file must be provided.')

if __name__ == "__main__":
    unittest.main()