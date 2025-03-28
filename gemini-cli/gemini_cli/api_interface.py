import os
from .gemini_api import GeminiAPI # Changed import to relative
from .utils import validate_file_path, validate_folder_path, read_file, process_image, setup_logger # Changed import to relative

# Initialize logger 
logger = setup_logger('api_interface')

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

    # Handle file input if provided
    if input_path:
        logger.info(f"Input path provided: {input_path}")
        if os.path.isdir(input_path):
            logger.info(f"Input path is a folder: {input_path}")
            validate_folder_path(input_path)
            # Handle folder input - for now just log it
            logger.info(f"Folder input processing is placeholder. Filter: {file_filter}")
            full_prompt = f"Using context from folder: {input_path} with filter: {file_filter}\n{prompt_text}"
        elif os.path.isfile(input_path):
            logger.info(f"Input path is a file: {input_path}")
            validate_file_path(input_path)
            # If generating image output from an image input
            if output_type == 'image':
                # Process the image if needed
                processed_image = process_image(input_path)
                try:
                    # Pass the resolved model_name directly
                    response = gemini_api.send_file_prompt(input_path, model=model_name)
                    return response.get('response', b"")  # Assuming image data is in response
                except Exception as e:
                    raise Exception(f"API request failed for image output: {e}") from e
            else: # output_type is text or default
                # If using a file as input for text generation
                try:
                    # Pass the resolved model_name directly
                    response = gemini_api.send_file_prompt(input_path, model=model_name)
                    logger.info("API call for file prompt successful.")
                except Exception as e:
                    raise Exception(f"API request failed for file prompt: {e}") from e
                return response.get('response', 'No response text found')
        else:
            logger.error(f"Input path is not a valid file or folder: {input_path}")
            raise ValueError(f"Invalid input path: {input_path}")
    else: # No file path, just text prompt
        full_prompt = prompt_text
        logger.debug(f"Full prompt content: {full_prompt[0:30]}...")
        try:
            # Pass the resolved model_name directly
            logger.info("Sending text prompt to API.")
            response = gemini_api.send_text_prompt(full_prompt, model=model_name)
        except Exception as e:
            raise Exception(f"API request failed for text prompt: {e}") from e

        # Extract text from response
        return response.get('response', 'No response text found')

    # If we reach here, there was an error in the inputs
    logger.error("Neither prompt nor file path provided.")
    raise ValueError("Either a prompt or file path must be provided.")