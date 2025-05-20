import json
import os

from google import genai
from google.genai import types
from google.genai.types import GenerateContentConfig

from .utils import process_doc, process_image, setup_logger, \
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
    elif file_type == 'doc':
        doc_data, mime_type = process_doc(file_path)  # Now returns data and mime_type
        if doc_data and mime_type:
            logger.info(f"Processed document file: {os.path.basename(file_path)} with MIME type {mime_type}")
            return types.Part.from_data(data=doc_data, mime_type=mime_type)
        else:
            # Handle case where mime_type couldn't be determined or data is None
            logger.error(f"Could not process document file properly: {file_path}")
            raise ValueError(f"Failed to process document file {file_path}")
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
            logger.info(f"Adding input: {file}")
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
        for file_info in input_files: # Renamed 'file' to 'file_info' for clarity
            logger.info(f"Adding input: {file_info}")
            contents.append(get_processed_file_content(file_info["path"], file_info["type"], self.client))

        config = GenerateContentConfig()
        config.response_modalities = ['Text', 'Image']

        if instructions:
            config.system_instruction = instructions

        # Handle image generation
        logger.debug(f"Using image generation with model: {model}")

        try:
            # Import the types module for configuration
            # from google.genai import types # This can be at the top of the file or class

            # Generate image content
            response = self.client.models.generate_content(
                model=model,
                contents=contents,  # <<< CORRECTED: Was 'prompt', should be the 'contents' list
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

    def generate_video_content(self, prompt, model, input_files=None, instructions=None, aspect_ratio="16:9", output_gcs=None, duration_seconds=5, person_generation="allow_adult", enhance_prompt=True, number_of_videos=1):
        """
        Generate a video using the Veo model.
        Args:
            prompt (str): Text prompt for the video.
            model (str): Model name (e.g., "veo-2.0-generate-001").
            input_files (list): Optional, for image input (GCS URI).
            instructions (str): Optional system instructions.
            aspect_ratio (str): "16:9" or "9:16".
            output_gcs (str): GCS URI for output video.
            duration_seconds (int): Duration of the video.
            person_generation (str): "allow_adult" or "dont_allow".
            enhance_prompt (bool): Whether to enhance the prompt.
            number_of_videos (int): Number of videos to generate.
        Returns:
            dict: Response with video URI or error.
        """
        from google.genai import types
        import time

        # If input_files is provided and is an image, use it as the image input
        image_part = None
        if input_files and len(input_files) > 0:
            image_file = input_files[0]
            # Assume input_files[0] is a dict with "gcs_uri" and "type"
            if image_file.get("type") == "image" and image_file.get("gcs_uri"):
                image_part = types.Image(
                    gcs_uri=image_file["gcs_uri"],
                    mime_type="image/png"
                )

        # Build config
        video_config = types.GenerateVideosConfig(
            aspect_ratio=aspect_ratio,
            output_gcs_uri=output_gcs,
            number_of_videos=number_of_videos,
            duration_seconds=duration_seconds,
            person_generation=person_generation,
            enhance_prompt=enhance_prompt,
        )

        # Prepare the operation call
        try:
            if image_part:
                operation = self.client.models.generate_videos(
                    model=model,
                    image=image_part,
                    config=video_config
                )
            else:
                operation = self.client.models.generate_videos(
                    model=model,
                    prompt=prompt,
                    config=video_config
                )

            # Wait for operation to complete
            while not operation.done:
                time.sleep(15)
                operation = self.client.operations.get(operation)

            # Extract video URI(s)
            if operation.response:
                video_uris = [v.video.uri for v in operation.result.generated_videos]
                return {
                    "video_uris": video_uris,
                    "model": model,
                    "prompt": prompt
                }
            else:
                return {
                    "error": "No video generated",
                    "model": model
                }
        except Exception as e:
            logger.error(f"Video generation error: {e}", exc_info=True)
            return {
                "error": str(e),
                "model": model
            }

    def delete_uploaded_files(self, file=None):
        if file is None:
            return
        self.client.files.delete(name=file)

    def uploaded_files(self):
        for f in self.client.files.list():
            print(' ', f.name)
