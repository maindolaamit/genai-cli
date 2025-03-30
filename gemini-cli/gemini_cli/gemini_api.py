import json

from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig

from .utils import process_image, setup_logger, \
    is_validate_file_size, process_pdf, process_audio, read_file, \
    validate_file_path  # Changed import to relative

# Initialize logger
logger = setup_logger('gemini_api')


def get_processed_file_content(file_path, file_type, client):
    """
    Process an input file based on its type.

    Args:
        file_path (str): Path to the file.
        file_type (str, optional): Type of file. If None, determined from extension.

    Returns:
        tuple: (processed_data, file_type)
        :param file_path:
        :param file_type:
        :param client:
    """
    # Check if a file exists and is within size limits
    validate_file_path(file_path)
    if not is_validate_file_size(file_path):
        return client.files.upload(file_path)

    # Process file based on its type
    if file_type == 'image':
        return process_image(file_path)
    elif file_type == 'pdf':
        pdf_data = process_pdf(file_path)
        return types.Part.from_bytes(
            data=pdf_data,
            mime_type='application/pdf',
        )
    elif file_type == 'text':
        return read_file(file_path)
    elif file_type == 'audio':
        audio_bytes = process_audio(file_path)
        return types.Part.from_bytes(
            data=audio_bytes,
            mime_type='audio/wav',
        )
    elif file_type == 'video':
        # video_bytes = process_video(file_path), file_type
        # return types.Part(
        #     inline_data=types.Blob(data=video_bytes, mime_type='video/mp4')
        # )
        # for video always upload the file
        return client.files.upload(file_path)
    else:
        raise ValueError(f"Unsupported file type: {file_type}")


class GeminiAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        # Initialize the Google Generative AI client
        self.client = genai.Client(api_key=api_key)

    def save_output(self, output, output_path):
        # Assuming output is text data for JSON saving. Adjust if binary.
        mode = 'w'
        data_to_save = output
        if isinstance(output, bytes):
            mode = 'wb'
        elif isinstance(output, dict) or isinstance(output, list):
            data_to_save = json.dumps(output, indent=4)
            mode = 'w'  # Ensure text mode for JSON string

        with open(output_path, mode) as f:
            f.write(data_to_save)

    @staticmethod
    def get_default_models():
        # This method might be less relevant now or could list model keys from cli.py's MODEL_MAP
        # For now, returning the hardcoded list as before.
        return ['gemini-pro', 'gemini-pro-vision', 'gemini-1.5-pro']

    def generate_text_content(self, prompt, model, input_files, instructions=None):
        # Assuming input_files is a list of file paths
        contents = [prompt]
        config = GenerateContentConfig()
        # loop for files and add to contents
        for file in input_files:
            logger.info(f"Processing file: {file}")
            contents.append(get_processed_file_content(file["path"], file["type"], self.client))

        if instructions:
            config.system_instruction = instructions

        # Handle text generation
        response = self.client.models.generate_content(
            model=model,
            contents=contents,
            config=config
        )

        # Return the text response
        return {
            'response': response.text,
            'model': model,
        }

    def generate_image_content(self, prompt, model, input_files, instructions=None):
        # Assuming input_files is a list of file paths
        contents = [prompt]
        # loop for files and add to contents
        for file in input_files:
            contents.append(get_processed_file_content(file.path, file.type))

        config = GenerateContentConfig()
        config.response_modalities = ['Text', 'Image']

        if instructions:
            config.system_instruction = instructions

        # Handle image generation
        logger.debug(f"Using image generation with model: {model}")

        try:
            # Import the types module for configuration
            from google.genai import types

            # Generate image content
            response = self.client.models.generate_content(
                model=model,
                contents=prompt,
                config=config
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

    def generate_audio_content(self, prompt, model, input_files, instructions=None):
        pass

    def generate_video_content(self, prompt, model, input_files, instructions=None):
        pass

    def delete_uploaded_files(self, file=None):
        if file is None:
            return
        self.client.files.delete(name=file)

    def uploaded_files(self):
        for f in self.client.files.list():
            print(' ', f.name)
