import argparse
import datetime  # Import datetime for timestamp
import os
import re
import signal
import sys

from .api_interface import interact_with_gemini_api
from .utils import setup_logger, read_file, validate_file_path  # Removed get_file_extension_from_mime

# Initialize logger
logger = setup_logger()


# Signal handler for graceful exit
def signal_handler(sig, frame):
    logger.info("Received signal to terminate. Cleaning up and exiting gracefully.")
    sys.exit(0)


# Register the signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Updated MODEL_MAP with capabilities
# Based on info from https://ai.google.dev/gemini-api/docs/models (as of late 2024/early 2025)
# Input types: 'text', 'image', 'audio', 'video', 'pdf', 'file' (generic for File API)
# Output types: 'text', 'image'
MODEL_MAP = {
    "flash": {
        "name": "gemini-2.0-flash",
        "inputs": ["text", "image", "audio", "video", "pdf", "file"],
        "outputs": ["text"],
        "default_output": "text"
    },
    "lite": {
        "name": "gemini-2.0-flash-lite",
        "inputs": ["text", "image", "audio", "video", "pdf", "file"],
        "outputs": ["text"],
        "default_output": "text"
    },
    "pro": {
        "name": "gemini-2.5-pro-exp-03-25",
        "inputs": ["text", "image", "audio", "video", "pdf", "file"],
        "outputs": ["text"],
        "default_output": "text"
    },
    "vision": {  # Mapping 'vision' to flash as a capable multimodal model
        "name": "gemini-1.5-flash-latest",
        "inputs": ["text", "image", "audio", "video", "pdf", "file"],
        "outputs": ["text"],
        "default_output": "text"
    },
    "imagen": {
        "name": "imagen-3.0-generate-002",  # Example name, verify actual latest Imagen model
        "inputs": ["text"],
        "outputs": ["image"],
        "default_output": "image"
    },
    "flash-img": {
        "name": "gemini-2.0-flash-exp-image-generation",  # Example name, verify actual latest Imagen model
        "inputs": ["text"],
        "outputs": ["image"],
        "default_output": "image"
    },
    # Add other aliases or models as needed
    "default": {  # Default maps to flash
        "name": "gemini-1.5-flash-latest",
        "inputs": ["text", "image", "audio", "video", "pdf", "file"],
        "outputs": ["text"],
        "default_output": "text"
    }
    # Removed less specific or potentially outdated mappings like 'lite', 'gemma', 'flash-img'
}

# Default model alias if -m is not specified
DEFAULT_MODEL_ALIAS = "default"


def generate_output_filename(model_name, prompt_text, output_type, output_dir=None):
    """Generates a filename based on prompt, model, timestamp, and output type.
    
    Args:
        model_name: The name of the model used
        prompt_text: Text of the prompt (for naming)
        output_type: Type of output (text, image, etc.)
        output_dir: Optional directory path to prepend
        
    Returns:
        Full path to the generated filename
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    # Extract first four words from prompt, lowercase, kebab-case
    prompt_words = prompt_text.split()[:4] if prompt_text else ["output"]
    kebab_prefix = "-".join(prompt_words).lower()
    kebab_prefix = re.sub(r'[^a-z0-9\-]+', '', kebab_prefix)  # Sanitize for filename

    # Determine file extension
    extension = "txt"  # Default
    if output_type == 'image':
        extension = "jpg"  # Assuming JPG for images, adjust if needed
    elif output_type == 'audio':
        extension = "mp3"
    elif output_type == 'video':
        extension = "mp4"

    # Sanitize model name for filename
    safe_model_name = model_name.replace('/', '_').replace('.', '_')

    filename = f"{kebab_prefix}_{safe_model_name}_{timestamp}.{extension}"

    # If output_dir is provided, join with the filename
    if output_dir:
        return os.path.join(output_dir, filename)
    else:
        return filename


def handle_output_path(output_path, model_name=None, prompt_text=None, output_type=None):
    if output_path is None and output_type == 'text':
        return None

    # Determine the actual output path
    if output_path == '' or (output_path is None and output_type != 'text'):
        # Empty -o flag, generate default filename
        output_path = generate_output_filename(model_name, prompt_text, output_type)
        logger.info(f"Empty output path specified, using generated filename: {output_path}")
    elif os.path.isdir(output_path):
        # If a directory was provided, generate filename in that directory
        output_path = generate_output_filename(model_name, prompt_text, output_type, output_path)
        logger.info(f"Directory specified for output, using: {output_path}")
    # Otherwise, use the provided path as-is

    # Ensure directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
        logger.info(f"Created output directory: {output_dir}")

    return output_path


def main():
    parser = argparse.ArgumentParser(description='Interact with the Gemini API.')

    # Prompt is now optional if input is provided
    parser.add_argument('-p', '--prompt', type=str, help='Text prompt or path to a file containing the prompt.')
    parser.add_argument('-i', '--input', type=str, help='Path to an input file or folder.')
    parser.add_argument('-f', '--filter', type=str,
                        help='Filter pattern for files in a folder (e.g., "*.txt", "*.jpg").')

    # Modified output argument to handle empty flag case
    parser.add_argument('-o', '--output', nargs='?', const='', default=None,
                        help='Optional path to save the output file. If flag is present with no value, a filename is auto-generated.')

    # Output type default is now None, will be inferred
    parser.add_argument('-t', '--output-type', choices=['text', 'image'], default=None,
                        help='Type of output to generate (default: inferred from model).')
    # Model default uses the constant
    parser.add_argument('-m', '--model', type=str, default=DEFAULT_MODEL_ALIAS,
                        help=f'Model alias to use (default: "{DEFAULT_MODEL_ALIAS}"). Choices: {", ".join(MODEL_MAP.keys())}')

    args = parser.parse_args()

    if not args.prompt and not args.input:
        logger.error('At least one of --prompt or --input must be provided.')
        parser.exit(1)

    if args.input and not os.path.exists(args.input):
        logger.error(f'The specified input path does not exist: {args.input}')
        parser.exit(1)

    # --- Process Prompt ---
    prompt_text = ""
    if args.prompt:
        if os.path.isfile(args.prompt):
            logger.info(f"Prompt argument '{args.prompt}' is a file path.")
            try:
                validate_file_path(args.prompt)  # Basic validation
                prompt_text = read_file(args.prompt)
                logger.info(f"Using content from file '{args.prompt}' as prompt.")
            except Exception as e:
                logger.error(f"Error reading prompt file '{args.prompt}': {e}")
                parser.exit(1)
        else:
            prompt_text = args.prompt
            logger.info("Using provided text as prompt.")

    # --- Output Handling ---
    output_path = args.output

    # --- Determine Output Type ---
    output_type = args.output_type

    # --- Model Selection and Validation ---
    model_alias = args.model

    # can be multiple models like -m flash, imagen
    model_aliases = model_alias.strip().split(',')
    # models_count = len(model_aliases)
    # if more than one model is specified, need to save the output even if not specified
    # if models_count > 1 and output_path is None:
    #     output_path = ''
    logger.info(f"Model aliases provided: {model_aliases}")

    # check if all aliases are valid
    for model_alias in model_aliases:
        model_details = MODEL_MAP.get(model_alias)
        model_name = model_details["name"]

        if not model_details:
            logger.error(
                f"Model alias '{model_alias}' not recognized. Valid aliases are: {', '.join(MODEL_MAP.keys())}")
            parser.exit(1)

        if output_type is None:
            output_type = model_details["default_output"]
            logger.info(f"Output type not specified, defaulting to model's default: '{output_type}'")
        else:
            # Validate if the requested output type is supported by the model
            if output_type not in model_details["outputs"]:
                logger.error(
                    f"Model '{model_name}' (alias: '{model_alias}') does not support the requested output type '{output_type}'. Supported types: {', '.join(model_details['outputs'])}")
                parser.exit(1)

        logger.info(f"Requested output type: '{output_type}'")
        # --- API Interaction ---
        generate_content_and_save(args, model_alias, model_details, output_type, parser, prompt_text, output_path)

    # Force a clean exit
    sys.exit(0)


def generate_content_and_save(args, model_alias, model_details, output_type, parser, prompt_text, output_path=None):
    model_name = model_details["name"]

    # Log the start of content generation
    logger.info("")
    logger.info("=========================================")
    logger.info("Starting content generation...")
    logger.info(f"Using model: {model_name} (alias: '{model_alias}')")
    try:
        # Pass the actual model name and determined output type
        response_data = interact_with_gemini_api(
            prompt=prompt_text,
            input_path=args.input,
            file_filter=args.filter,
            output_type=output_type,  # Pass determined output type
            model_name=model_name,  # Pass actual model name
            model_capabilities=model_details  # Pass capabilities for potential use in api_interface
        )

        if response_data is None:
            logger.error("API interaction failed to return data.")
            sys.exit(1)

        # --- Output Handling ---
        output_path = handle_output_path(output_path, model_name, prompt_text, output_type)

        is_binary_output = isinstance(response_data, bytes)

        # For text output: print to console by default, save to file ONLY if -o is specified
        if output_type == 'text' and not is_binary_output:
            # Always print text output to console
            print(response_data)

            # Only save to file if -o was provided (either empty or with value)
            if output_path is not None:
                # Save the file
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(response_data)
                    logger.info(f"Text output saved to {output_path}")
                except IOError as e:
                    logger.error(f"Failed to write output to {output_path}: {e}")
                    sys.exit(1)
        else:
            # Write binary output to file
            try:
                with open(output_path, 'wb') as f:
                    f.write(response_data)
                logger.info(f"Output successfully saved to {output_path}")
            except IOError as e:
                logger.error(f"Failed to write output to {output_path}: {e}")
                sys.exit(1)
            except Exception as e:
                logger.error(f"An unexpected error occurred while writing output: {e}")
                sys.exit(1)

    except Exception as e:
        logger.error(f"An error occurred during API interaction or processing: {e}", exc_info=True)
        parser.exit(1)


if __name__ == '__main__':
    main()
