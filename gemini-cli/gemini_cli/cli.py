import argparse
import os
import logging
import time
import re
import datetime  # Import datetime for timestamp
from .api_interface import interact_with_gemini_api
from .utils import setup_logger, read_file, validate_file_path 

# Initialize logger
logger = setup_logger()

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
    "vision": { # Mapping 'vision' to flash as a capable multimodal model
        "name": "gemini-1.5-flash-latest",
        "inputs": ["text", "image", "audio", "video", "pdf", "file"],
        "outputs": ["text"],
        "default_output": "text"
    },
    "imagen": {
        "name": "imagen-3.0-generate-002", # Example name, verify actual latest Imagen model
        "inputs": ["text"],
        "outputs": ["image"],
        "default_output": "image"
    },
    "flash-img": {
        "name": "gemini-2.0-flash-exp-image-generation", # Example name, verify actual latest Imagen model
        "inputs": ["text"],
        "outputs": ["image"],
        "default_output": "image"
    },
    # Add other aliases or models as needed
    "default": { # Default maps to flash
        "name": "gemini-1.5-flash-latest",
        "inputs": ["text", "image", "audio", "video", "pdf", "file"],
        "outputs": ["text"],
        "default_output": "text"
    }
    # Removed less specific or potentially outdated mappings like 'lite', 'gemma', 'flash-img'
}

# Default model alias if -m is not specified
DEFAULT_MODEL_ALIAS = "default"

def generate_output_filename(model_name, prompt_text, output_type):
    """Generates a filename based on model, prompt, timestamp, and output type."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    
    # Extract first four words from prompt, lowercase, kebab-case
    prompt_words = prompt_text.split()[:4] if prompt_text else ["output"]
    kebab_prefix = "-".join(prompt_words).lower()
    kebab_prefix = re.sub(r'[^a-z0-9\-]+', '', kebab_prefix) # Sanitize for filename

    # Determine file extension
    extension = "txt" # Default
    if output_type == 'image':
        extension = "jpg" # Assuming JPG for images, adjust if needed
    # Add more extensions for audio/video if supported later
    
    # Sanitize model name for filename
    safe_model_name = model_name.replace('/', '_').replace('.', '_')

    return f"{safe_model_name}_{kebab_prefix}_{timestamp}.{extension}"

def main():
    parser = argparse.ArgumentParser(description='Interact with the Gemini API.')

    # Prompt is now optional if input is provided
    parser.add_argument('-p', '--prompt', type=str, help='Text prompt or path to a file containing the prompt.')
    parser.add_argument('-i', '--input', type=str, help='Path to an input file or folder.')
    parser.add_argument('-f', '--filter', type=str, help='Filter pattern for files in a folder (e.g., "*.txt", "*.jpg").')
    # Output is optional
    parser.add_argument('-o', '--output', type=str, default=None, help='Optional path to save the output file. If omitted, a filename is generated.')
    # Output type default is now None, will be inferred
    parser.add_argument('-t', '--output-type', choices=['text', 'image'], default=None, help='Type of output to generate (default: inferred from model).')
    # Model default uses the constant
    parser.add_argument('-m', '--model', type=str, default=DEFAULT_MODEL_ALIAS, help=f'Model alias to use (default: "{DEFAULT_MODEL_ALIAS}"). Choices: {", ".join(MODEL_MAP.keys())}')

    args = parser.parse_args()

    if not args.prompt and not args.input:
        logger.error('At least one of --prompt or --input must be provided.')
        parser.exit(1)

    if args.input and not os.path.exists(args.input):
        logger.error(f'The specified input path does not exist: {args.input}')
        parser.exit(1)

    # --- Model Selection and Validation ---
    model_alias = args.model
    model_details = MODEL_MAP.get(model_alias)

    if not model_details:
        logger.error(f"Model alias '{model_alias}' not recognized. Valid aliases are: {', '.join(MODEL_MAP.keys())}")
        parser.exit(1)

    model_name = model_details["name"]
    logger.info(f"Using model: {model_name} (alias: '{model_alias}')")

    # --- Determine Output Type ---
    output_type = args.output_type
    if output_type is None:
        output_type = model_details["default_output"]
        logger.info(f"Output type not specified, defaulting to model's default: '{output_type}'")
    else:
        # Validate if the requested output type is supported by the model
        if output_type not in model_details["outputs"]:
            logger.error(f"Model '{model_name}' (alias: '{model_alias}') does not support the requested output type '{output_type}'. Supported types: {', '.join(model_details['outputs'])}")
            parser.exit(1)
        logger.info(f"Requested output type: '{output_type}'")

    # --- Process Prompt ---
    prompt_text = ""
    if args.prompt:
        if os.path.isfile(args.prompt):
            logger.info(f"Prompt argument '{args.prompt}' is a file path.")
            try:
                validate_file_path(args.prompt) # Basic validation
                prompt_text = read_file(args.prompt)
                logger.info(f"Using content from file '{args.prompt}' as prompt.")
            except Exception as e:
                logger.error(f"Error reading prompt file '{args.prompt}': {e}")
                parser.exit(1)
        else:
            prompt_text = args.prompt
            logger.info("Using provided text as prompt.")

    # --- API Interaction ---
    try:
        # Pass the actual model name and determined output type
        response_data = interact_with_gemini_api(
            prompt=prompt_text,
            input_path=args.input,
            file_filter=args.filter,
            output_type=output_type, # Pass determined output type
            model_name=model_name,   # Pass actual model name
            model_capabilities=model_details # Pass capabilities for potential use in api_interface
        )

        if response_data is None:
             logger.error("API interaction failed to return data.")
             parser.exit(1)

        # --- Output Handling ---
        output_path = args.output
        is_binary_output = isinstance(response_data, bytes)

        if output_path is None:
            # Generate filename if output path is not provided
            output_path = generate_output_filename(model_name, prompt_text, output_type)
            logger.info(f"Output path not specified, saving to generated filename: {output_path}")

        # Ensure directory exists if output path includes directories
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
                logger.info(f"Created output directory: {output_dir}")
            except OSError as e:
                logger.error(f"Failed to create output directory {output_dir}: {e}")
                parser.exit(1)

        # Write output to file
        try:
            write_mode = 'wb' if is_binary_output else 'w'
            encoding = None if is_binary_output else 'utf-8'
            with open(output_path, write_mode, encoding=encoding) as f:
                f.write(response_data)
            logger.info(f"Output successfully saved to {output_path}")
        except IOError as e:
            logger.error(f"Failed to write output to {output_path}: {e}")
            parser.exit(1)
        except Exception as e:
             logger.error(f"An unexpected error occurred while writing output: {e}")
             parser.exit(1)

    except Exception as e:
        logger.error(f"An error occurred during API interaction or processing: {e}", exc_info=True)
        parser.exit(1)


if __name__ == '__main__':
    main()