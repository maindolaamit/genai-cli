import os

from .gemini_api import GeminiAPI
from .utils import (
    validate_file_path, validate_folder_path, get_file_type, get_files_from_folder, setup_logger
)

# Initialize logger 
logger = setup_logger('api_interface')

ALLOWED_FILE_COUNT = 5  # Maximum number of files to process at once


def get_input_files(input_path, file_filter, model_name, allowed_file_types=None):
    """
    Get input files based on the provided input path and filter.

    :param model_name:
    :param input_path:
    :param file_filter:
    :param allowed_file_types:
    :return:
    """
    if allowed_file_types is None:
        allowed_file_types = []
    if not input_path:
        return []

    # Handle multimodal or text models with file/folder input
    logger.info(f"Input path provided: {input_path}")
    files = []

    # --- Folder Input Logic ---
    if os.path.isdir(input_path):
        logger.info(f"Input path is a folder: {input_path}")
        validate_folder_path(input_path)
        files = get_files_from_folder(input_path, file_filter)
        if not files:
            raise ValueError(f"No matching files found in folder: {input_path}")
        logger.info(f"Found {len(files)} matching files in folder")
    # --- Single File Input Logic ---
    elif os.path.isfile(input_path):
        logger.info(f"Input path is a file: {input_path}")
        validate_file_path(input_path)
        files.append(input_path)
    else:
        raise ValueError(f"Invalid input path: {input_path}")

    # Handle text-only prompt (no file input) for text models
    processed_files = []
    count = 1
    for file_path in files:
        try:
            file_type = get_file_type(file_path)
            if file_type and file_type in allowed_file_types:
                logger.info(f"Processing file: {file_path} (type: {file_type})")
                processed_files.append({
                    'path': file_path,
                    'type': file_type,
                })
                count += 1
            elif file_type:
                logger.warning(
                    f"Skipping file {file_path}: type '{file_type}' not supported by model '{model_name}'")
        except Exception as e:
            logger.warning(f"Error processing file {file_path}: {e}")

    return processed_files[:ALLOWED_FILE_COUNT]


def interact_with_gemini_api(prompt, input_path, file_filter, output_type, model_name, model_capabilities):
    """
    Interact with the Gemini API based on the provided arguments.

    Args:
        prompt (str): Text prompt to send to the API.
        input_path (str): Path to an input file or folder.
        file_filter (str): Filter for files in the folder.
        output_type (str): The type of output to generate ('text' or 'image').
        model_name (str): The actual Gemini model name string (e.g., 'gemini-1.5-pro-latest').
        model_capabilities (dict): Dictionary containing model input/output capabilities.

    Returns:
        str or bytes: The API response as text or binary data.
    """
    # Get API key from environment variable
    api_key = os.environ.get('GEMINI_API_KEY')
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY environment variable is not set. "
            "Please set it to your Gemini API key."
        )

    # Initialize the Gemini API client
    gemini_api = GeminiAPI(api_key)

    # Process prompt text (if it's a string or file)
    prompt_text = prompt

    input_files = get_input_files(input_path, file_filter, model_name)

    # --- Determine API call based on input and model capabilities ---
    if output_type == 'text':
        try:
            response = gemini_api.generate_text_content(
                prompt=prompt_text,
                model=model_name,
                input_files=input_files,
            )
            return response.get('response', 'No response text found' if output_type == 'text' else b'')
        except Exception as e:
            raise Exception(f"API request failed for folder input: {e}") from e
    elif output_type == 'image':
        try:
            response = gemini_api.generate_image_content(
                prompt=prompt_text,
                model=model_name,
                input_files=input_files,
            )
            return response
        except Exception as e:
            raise Exception(f"API request failed for folder input: {e}") from e
    elif output_type == 'audio':
        try:
            response = gemini_api.generate_audio_content(
                prompt=prompt_text,
                model=model_name,
                input_files=input_files,
            )
            return response
        except Exception as e:
            raise Exception(f"API request failed for folder input: {e}") from e
    elif output_type == 'video':
        try:
            response = gemini_api.generate_video_content(
                prompt=prompt_text,
                model=model_name,
                input_files=input_files,
            )
            return response
        except Exception as e:
            raise Exception(f"API request failed for folder input: {e}") from e
    else:
        raise ValueError(f"Unsupported output type: {output_type}")
