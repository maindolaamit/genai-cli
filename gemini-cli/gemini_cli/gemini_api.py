import json
from google import genai
from PIL import Image
import os
from .utils import (
    validate_file_path, validate_folder_path, read_file, 
    process_image, process_pdf, process_text_file, process_audio, process_video,
    get_file_type, setup_logger, FILE_FORMATS
)

# Initialize logger
logger = setup_logger('gemini_api')

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

    def send_file_prompt(self, file_path, prompt=None, model='gemini-pro-vision', output_type='text'):
        """
        Sends a file prompt to the specified Gemini model.
        
        Args:
            file_path (str): Path to the file to process.
            prompt (str, optional): Additional text prompt to send with the file.
            model (str): The Gemini model to use.
            output_type (str): Type of output to generate ('text' or 'image').
            
        Returns:
            dict: Response containing 'response' and 'model' keys.
        """
        try:
            # Validate file exists
            validate_file_path(file_path)
            
            # Get the file type
            file_type = get_file_type(file_path)
            if not file_type:
                raise ValueError(f"Unsupported file type for {file_path}")
                
            logger.info(f"Processing file type: {file_type} for model: {model}")
            
            # Create a prompt text based on user input or default
            prompt_text = prompt if prompt else f"Describe this {file_type} in detail:"
            
            # Process file based on type
            if file_type == 'image':
                # Process image using the genai.Image class
                try:
                    from google.genai import Image as GenAIImage
                    image_obj = GenAIImage.load_from_file(file_path)
                    
                    # Create content for the API request
                    response = self.client.models.generate_content(
                        model=model,
                        contents=[prompt_text, image_obj]
                    )
                except ImportError:
                    # If the Google GenAI Image class is not available, fallback to direct base64
                    import base64
                    with open(file_path, "rb") as f:
                        image_bytes = f.read()
                    
                    image_parts = [
                        {"text": prompt_text},
                        {"inline_data": {"mime_type": "image/jpeg", "data": base64.b64encode(image_bytes).decode("utf-8")}}
                    ]
                    
                    response = self.client.models.generate_content(
                        model=model,
                        contents=image_parts
                    )
                    
            elif file_type == 'text':
                # Process text file
                text_data = process_text_file(file_path)
                response = self.client.models.generate_content(
                    model=model,
                    contents=[{"text": prompt_text + "\n\n" + text_data}]
                )
                
            elif file_type == 'pdf':
                # For PDF files, we'll need to use blob or file handling depending on API support
                logger.info("Processing PDF file")
                # This implementation assumes the gemini-pro-vision model can process PDFs
                response = self.client.models.generate_content(
                    model=model,
                    contents=[
                        {"text": prompt_text},
                        {"file_data": {"file_uri": file_path, "mime_type": "application/pdf"}}
                    ]
                )
                
            elif file_type in ['audio', 'video']:
                # For audio/video, may need specialized handling
                logger.info(f"Processing {file_type} file")
                mime_type = f"{file_type}/{os.path.splitext(file_path)[1].lower().lstrip('.')}"
                response = self.client.models.generate_content(
                    model=model,
                    contents=[
                        {"text": prompt_text},
                        {"file_data": {"file_uri": file_path, "mime_type": mime_type}}
                    ]
                )
            else:
                raise ValueError(f"File type {file_type} processing not implemented")
                
            # Return response based on output type
            logger.info("Processing API response")
            if output_type == 'image':
                # For image generation - handle accordingly
                return {
                    'response': response.text if hasattr(response, 'text') else response,
                    'model': model
                }
            else:
                # For text responses
                return {
                    'response': response.text if hasattr(response, 'text') else str(response),
                    'model': model
                }
                    
        except Exception as e:
            # Provide more context in the error message
            raise Exception(f"Error sending {file_type if 'file_type' in locals() else 'file'} prompt to Gemini model '{model}': {e}") from e

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