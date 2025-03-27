import os
from .gemini_api import GeminiAPI # Changed import to relative
from .utils import validate_file_path, validate_folder_path, read_file, process_image, setup_logger # Changed import to relative

# Initialize logger 
logger = setup_logger('api_interface')

def interact_with_gemini_api(prompt, file_path, folder_path, output_type, model_name):
    """
    Interact with the Gemini API based on the provided arguments.

    Args:
        prompt (str): Text prompt to send to the API.
        file_path (str): Path to a file to attach.
        folder_path (str): Path to a folder containing additional context files.
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

    # Process the folder context if provided
    folder_context = ""
    if folder_path:
        validate_folder_path(folder_path)
        # Here we would process the folder to extract context
        # This is a placeholder for folder context processing
        folder_context = f"Using context from folder: {folder_path}\n"

    # Combine prompt with folder context
    full_prompt = f"{folder_context}{prompt or ''}"

    # Handle file input if provided
    if file_path:
        validate_file_path(file_path)
        # If generating image output from an image input
        if output_type == 'image':
            # Process the image if needed
            processed_image = process_image(file_path)
            try:
                # Pass the resolved model_name directly
                response = gemini_api.send_file_prompt(file_path, model=model_name)
                return response.get('response', b"")  # Assuming image data is in response
            except Exception as e:
                raise Exception(f"API request failed for image output: {e}") from e

        # If using a file as input for text generation
        try:
            # Pass the resolved model_name directly
            response = gemini_api.send_file_prompt(file_path, model=model_name)
        except Exception as e:
            raise Exception(f"API request failed for file prompt: {e}") from e

        # Extract text from response (assuming API returns JSON with a text field)
        # This structure will depend on the actual Gemini API response format
        return response.get('response', 'No response text found')

    # If no file, use the text prompt
    if full_prompt:
        try:
            # Pass the resolved model_name directly
            response = gemini_api.send_text_prompt(full_prompt, model=model_name)
        except Exception as e:
            raise Exception(f"API request failed for text prompt: {e}") from e

        # Extract text from response
        return response.get('response', 'No response text found')

    # If we reach here, there was an error in the inputs
    raise ValueError("Either a prompt or file path must be provided.")