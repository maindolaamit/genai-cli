import argparse
import os
import json
from google import genai
from PIL import Image
from utils import validate_file_path, validate_folder_path, read_file, process_image
class GeminiAPI:
    def __init__(self, api_key, base_url=None):
        self.api_key = api_key
        # Ensure genai is configured correctly. Assuming API key needs to be set.
        # If using google.genai directly, configuration might be needed.
        # Check google-genai documentation for the correct way to initialize/configure.
        self.client = genai.Client(api_key=api_key) 

        # # Configure the library with the API key if needed by the library structure
        # try:
        #      genai.configure(api_key=api_key)
        # except Exception as e:
        #      print(f"Warning: Could not configure google.genai with API key: {e}")


    def send_text_prompt(self, prompt, model='gemini-1.5-flash'): # Default model string
        """Sends a text prompt to the specified Gemini model."""
        try:

            # Generate content using the model
            response = self.client.models.generate_content(
                model=model, # Use the provided model string directly
                contents=prompt,
            )

            # Return the response in a consistent format
            return {
                'response': response.text,
                'model': model # Return the model name used
            }
        except Exception as e:
            # Provide more context in the error message
            raise Exception(f"Error sending text prompt to Gemini model '{model}': {e}") from e

    def send_file_prompt(self, file_path, model='gemini-pro-vision'): # Default model string
        """Sends a file (image) prompt to the specified Gemini model."""
        try:
            # Load the image file
            image = Image.open(file_path)
            
            # Prepare content parts (image with optional description)
            parts = [
                {"text": "Describe the content of the image:"},
                {"image": {"data": process_image(file_path)}}
            ]
            
            # Use the models.generate_content method from the client directly
            response = self.client.models.generate_content(
                model=model,
                contents=parts
            )

            # Return the response in a consistent format
            return {
                'response': response.text,
                'model': model # Return the model name used
            }
        except Exception as e:
             # Provide more context in the error message
            raise Exception(f"Error sending file prompt to Gemini model '{model}': {e}") from e

    def save_output(self, output, output_path):
        # Assuming output is text data for JSON saving. Adjust if binary.
        mode = 'w'
        data_to_save = output
        if isinstance(output, bytes):
             mode = 'wb'
        elif isinstance(output, dict) or isinstance(output, list):
             data_to_save = json.dumps(output, indent=4)
             mode = 'w' # Ensure text mode for JSON string

        with open(output_path, mode) as f:
             f.write(data_to_save)


    def get_default_models(self):
        # This method might be less relevant now or could list model keys from cli.py's MODEL_MAP
        # For now, returning the hardcoded list as before.
        return ['gemini-pro', 'gemini-pro-vision', 'gemini-1.5-pro']