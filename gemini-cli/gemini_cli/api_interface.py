import os
from .gemini_api import GeminiAPI
from .utils import (
    validate_file_path, validate_folder_path, read_file, 
    process_image, process_pdf, process_text_file, process_audio, process_video,
    get_file_type, validate_file_size, get_files_from_folder, validate_file_type,
    setup_logger, FILE_FORMATS
)

# Initialize logger 
logger = setup_logger('api_interface')

def process_input_file(file_path, file_type=None):
    """
    Process an input file based on its type.
    
    Args:
        file_path (str): Path to the file.
        file_type (str, optional): Type of file. If None, determined from extension.
    
    Returns:
        tuple: (processed_data, file_type)
    """
    # Validate file exists and is within size limits
    validate_file_path(file_path)
    validate_file_size(file_path)
    
    # Determine file type if not provided
    if file_type is None:
        file_type = get_file_type(file_path)
        if file_type is None:
            extension = os.path.splitext(file_path)[1].lower()
            raise ValueError(f"Unsupported file type: {extension}")
    
    # Process file based on its type
    if file_type == 'image':
        return process_image(file_path), file_type
    elif file_type == 'pdf':
        return process_pdf(file_path), file_type
    elif file_type == 'text':
        return process_text_file(file_path), file_type
    elif file_type == 'audio':
        return process_audio(file_path), file_type
    elif file_type == 'video':
        return process_video(file_path), file_type
    else:
        raise ValueError(f"Unsupported file type: {file_type}")

def interact_with_gemini_api(prompt, input_path, file_filter, output_type, model_name):
    """
    Interact with the Gemini API based on the provided arguments.

    Args:
        prompt (str): Text prompt to send to the API.
        input_path (str): Path to an input file or folder.
        file_filter (str): Filter for files in the folder.
        output_type (str): The type of output to generate ('text' or 'image').
        model_name (str): The actual Gemini model name string (e.g., 'gemini-1.5-pro').

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
    prompt_text = ""
    if prompt:
        if os.path.isfile(prompt):
            logger.info(f"Prompt '{prompt}' is a file path.")
            try:
                validate_file_path(prompt)
                prompt_text = read_file(prompt)
                logger.info(f"Using content from file '{prompt}' as prompt.")
            except FileNotFoundError as e:
                logger.error(f"File not found error for prompt file '{prompt}'.")
                logger.error(f"Error: Prompt file not found: {e}")
                return None
            except Exception as e:
                logger.error(f"An unexpected error occurred while reading prompt file: {e}")
                return None
        else:
            # Use the prompt as-is if it's not a file path
            prompt_text = prompt

    # Handle file or folder input if provided
    if input_path:
        logger.info(f"Input path provided: {input_path}")
        
        # Handle folder input
        if os.path.isdir(input_path):
            logger.info(f"Input path is a folder: {input_path}")
            validate_folder_path(input_path)
            
            # Get files from folder with optional filter
            files = get_files_from_folder(input_path, file_filter)
            
            if not files:
                logger.warning(f"No matching files found in folder: {input_path}")
                raise ValueError(f"No matching files found in folder: {input_path}")
            
            logger.info(f"Found {len(files)} matching files in folder")
            
            # Process each file based on its type
            processed_files = []
            for file_path in files:
                try:
                    file_type = get_file_type(file_path)
                    if file_type:
                        logger.info(f"Processing file: {file_path} (type: {file_type})")
                        processed_data, _ = process_input_file(file_path, file_type)
                        processed_files.append({
                            'path': file_path,
                            'type': file_type,
                            'data': processed_data
                        })
                except Exception as e:
                    logger.warning(f"Error processing file {file_path}: {e}")
            
            if not processed_files:
                logger.error("No files could be processed from the folder.")
                raise ValueError("No files could be processed from the folder.")
            
            # Handle the processed files (currently only handling the first file)
            # In the future, this could be enhanced to handle multiple files
            if processed_files:
                first_file = processed_files[0]
                logger.info(f"Using first file for API request: {first_file['path']}")
                
                try:
                    response = gemini_api.send_file_prompt(
                        first_file['path'], 
                        prompt=prompt_text,
                        model=model_name
                    )
                    return response.get('response', 'No response text found')
                except Exception as e:
                    raise Exception(f"API request failed for folder input: {e}") from e
        
        # Handle single file input
        elif os.path.isfile(input_path):
            logger.info(f"Input path is a file: {input_path}")
            validate_file_path(input_path)
            
            try:
                # Get file type and validate it
                file_type = get_file_type(input_path)
                if not file_type:
                    raise ValueError(f"Unsupported file type for {input_path}")
                
                logger.info(f"File type detected: {file_type}")
                
                # Ensure file size is within limits
                validate_file_size(input_path)
                
                # Process file based on its type and output type
                if output_type == 'image':
                    # If generating image output, make sure we're using an appropriate model
                    if 'imagen' not in model_name.lower():
                        logger.warning(f"Image output requested but model {model_name} may not support image generation")
                    
                    logger.info(f"Sending prompt for image generation")
                    response = gemini_api.send_file_prompt(
                        input_path, 
                        prompt=prompt_text,
                        model=model_name, 
                        output_type='image'
                    )
                    return response.get('response', b"")  # Return binary image data
                else:
                    # For text output, process file based on its type
                    logger.info(f"Processing file for text generation: {input_path}")
                    
                    response = gemini_api.send_file_prompt(
                        input_path, 
                        prompt=prompt_text,
                        model=model_name
                    )
                    logger.info("API call for file prompt successful")
                    return response.get('response', 'No response text found')
            
            except Exception as e:
                raise Exception(f"Error processing input file: {e}") from e
        
        else:
            logger.error(f"Input path is not a valid file or folder: {input_path}")
            raise ValueError(f"Invalid input path: {input_path}")
    
    # Handle text-only prompt (no file input)
    else:
        if not prompt_text:
            logger.error("Neither prompt nor input path provided")
            raise ValueError("Either a prompt or input path must be provided")
        
        logger.info(f"Sending text-only prompt to API")
        try:
            response = gemini_api.send_text_prompt(prompt_text, model=model_name)
            return response.get('response', 'No response text found')
        except Exception as e:
            raise Exception(f"API request failed for text prompt: {e}") from e