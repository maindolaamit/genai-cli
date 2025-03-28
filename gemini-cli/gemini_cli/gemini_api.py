import json
from google import genai
from PIL import Image
from io import BytesIO
from .utils import validate_file_path, validate_folder_path, read_file, process_image, setup_logger # Changed import to relative

# Initialize logger
logger = setup_logger('gemini_api')

class GeminiAPI:
    def __init__(self, api_key, base_url=None):
        self.api_key = api_key
        # Initialize the Google Generative AI client
        self.client = genai.Client(api_key=api_key) 

    def send_text_prompt(self, prompt, model='gemini-1.5-flash', output_type='text'): # Default model string
        """Sends a text prompt to the specified Gemini model."""
        try:
            # Check if model is for image generation
            is_image_model = 'imagen' in model.lower() or 'image-generation' in model.lower()
            logger.debug(f"Using model: {model} for {'image' if is_image_model else 'text'} generation")
            
            if is_image_model or output_type == 'image':
                # Handle image generation
                logger.debug(f"Using image generation with model: {model}")
                
                try:
                    # Import the types module for configuration
                    from google.genai import types
                    
                    # Generate image content
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_modalities=['Text', 'Image']
                        )
                    )
                    
                    # Process the response to extract the image
                    image_data = None
                    text_response = ""
                    
                    for part in response.candidates[0].content.parts:
                        if part.text is not None:
                            text_response += part.text
                        elif part.inline_data is not None:
                            logger.debug("Found image data in response part")
                            image_data = part.inline_data.data
                    
                    if image_data:
                        return {
                            'response': image_data,  # Return binary image data
                            'text_response': text_response,  # Include any text response
                            'model': model
                        }
                    else:
                        logger.warning("No image data found in response parts")
                        return {
                            'response': text_response.encode('utf-8') if text_response else b'',
                            'model': model,
                            'warning': "No image data found in response"
                        }
                    
                except Exception as gen_error:
                    logger.error(f"Error in image generation: {str(gen_error)}", exc_info=True)
                    error_message = f"Image generation error: {str(gen_error)}"
                    return {
                        'response': error_message.encode('utf-8'),
                        'model': model,
                        'error': str(gen_error)
                    }
            else:
                # For text models, generate content as before
                response = self.client.models.generate_content(
                    model=model,
                    contents=prompt,
                )
                
                # Return the text response
                return {
                    'response': response.text,
                    'model': model
                }
        except Exception as e:
            # Provide more context in the error message
            logger.error(f"Error in send_text_prompt: {str(e)}", exc_info=True)
            error_message = f"Error sending prompt to model: {str(e)}"
            return {
                'response': error_message.encode('utf-8'),
                'model': model,
                'error': str(e)
            }

    # Add 'prompt' and 'output_type' to the signature
    def send_file_prompt(self, file_path, prompt=None, model='gemini-pro-vision', output_type='text'): 
        """Sends a file (image) prompt to the specified Gemini model."""
        try:
            # Check if model is for image generation
            is_image_model = 'imagen' in model.lower() or 'image-generation' in model.lower()
            
            # Load the image file
            image = Image.open(file_path)
            
            if is_image_model:
                # For image generation models, use similar approach as in send_text_prompt
                logger.debug(f"Using image generation with model: {model}")
                
                try:
                    from google.genai import types
                    
                    # Read file content to use as prompt
                    with open(file_path, 'r') as f:
                        prompt = f.read().strip()
                    
                    # Generate image content
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt,
                        config=types.GenerateContentConfig(
                            response_modalities=['Text', 'Image']
                        )
                    )
                    
                    # Process the response to extract the image
                    image_data = None
                    text_response = ""
                    
                    for part in response.candidates[0].content.parts:
                        if part.text is not None:
                            text_response += part.text
                        elif part.inline_data is not None:
                            logger.debug("Found image data in response part")
                            image_data = part.inline_data.data
                    
                    if image_data:
                        return {
                            'response': image_data,  # Return binary image data
                            'text_response': text_response,  # Include any text response
                            'model': model
                        }
                    else:
                        logger.warning("No image data found in response parts")
                        return {
                            'response': text_response.encode('utf-8') if text_response else b'',
                            'model': model,
                            'warning': "No image data found in response"
                        }
                except Exception as gen_error:
                    logger.error(f"Error in image generation: {str(gen_error)}", exc_info=True)
                    error_message = f"Image generation error: {str(gen_error)}"
                    return {
                        'response': error_message.encode('utf-8'),
                        'model': model,
                        'error': str(gen_error)
                    }
            else:
                # For vision models (like gemini-pro-vision)
                # Prepare content parts (image with optional description)
                parts = []
                # Use the provided prompt text if available
                if prompt:
                    parts.append({"text": prompt})
                else:
                    # Default text if no prompt is given
                    parts.append({"text": "Describe the content of the image:"}) 
                
                # Add the image data (assuming process_image handles conversion)
                # You might need to adjust how image data is prepared based on google-genai requirements
                # For google-genai, you typically pass the PIL Image object directly
                try:
                    img = Image.open(file_path)
                    parts.append(img) # Pass the PIL image object
                except Exception as img_err:
                    logger.error(f"Error opening or processing image {file_path}: {img_err}")
                    raise Exception(f"Failed to load image {file_path}") from img_err

                # Use the models.generate_content method from the client directly
                response = self.client.models.generate_content(
                    model=model,
                    contents=parts
                )

                # Return response (text for vision models)
                return {
                    'response': response.text if hasattr(response, 'text') else str(response),
                    'model': model
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