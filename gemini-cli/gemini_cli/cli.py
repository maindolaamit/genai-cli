import argparse
import os
import logging # Import logging
from .api_interface import interact_with_gemini_api # Changed import to relative
from .utils import setup_logger # Changed import to relative

# Initialize logger
logger = setup_logger()

MODEL_MAP = {
    "default": "gemini-1.5-pro-latest",
    "flash": "gemini-1.5-pro",
    "vision": "gemini-1.0-pro-vision-latest",
    "imagen": "imagen-3.0-generate-002",
    "unknown-model": "gemini-unknown"
}

DEFAULT_TEXT_MODEL = "default"
DEFAULT_IMAGE_MODEL = "vision"

def main():
    parser = argparse.ArgumentParser(description='Interact with the Gemini API.')

    required = parser.add_argument_group('required arguments')
    required.add_argument('-p', '--prompt', type=str, help='Text prompt to send to the API.')

    parser.add_argument('-i', '--input', type=str, help='Path to an input file or folder.')
    parser.add_argument('-f', '--filter', type=str, help='Filter pattern for files in a folder (e.g., "*.txt", "*.jpg").')
    parser.add_argument('-o', '--output', type=str, help='Path to save the output file.')
    parser.add_argument('-t', '--output-type', choices=['text', 'image'], default='text', help='Type of output to generate.')
    parser.add_argument('-m', '--model', type=str, default=None, help='Model code to use for the API request.')

    args = parser.parse_args()

    if not args.prompt and not args.input:
        # Use logger.error instead of parser.error for consistency if desired,
        # or keep parser.error for its specific behavior (prints usage and exits).
        logger.error('At least one of --prompt or --input must be provided.')
        parser.exit(1) # Manually exit if using logger.error

    if args.input and not os.path.exists(args.input):
        logger.error(f'The specified input path does not exist: {args.input}')
        parser.exit(1)

    # Determine model based on output type and user input
    if args.model:
        model_name = MODEL_MAP.get(args.model)
        if not model_name:
            logger.error(f"Model code '{args.model}' not recognized. Valid model codes are: {', '.join(MODEL_MAP.keys())}")
            parser.exit(1)
    else:
        default_model_key = DEFAULT_TEXT_MODEL if args.output_type == 'text' else DEFAULT_IMAGE_MODEL
        model_name = MODEL_MAP.get(default_model_key)

    if not model_name:
        logger.warning(f"No specific default model found for output type '{args.output_type}'. Falling back to general default.")
        model_name = MODEL_MAP["default"] # Fallback to default

    logger.info(f"Using model: {model_name}") # Use logger.info

    try:
        response = interact_with_gemini_api(args.prompt, args.input, args.filter, args.output_type, model_name)

        if args.output:
            try:
                with open(args.output, 'wb' if args.output_type == 'image' else 'w') as f:
                    f.write(response)
                logger.info(f"Output saved to {args.output}") # Use logger.info
            except IOError as e:
                logger.error(f"Failed to write output to {args.output}: {e}") # Use logger.error
        else:
             # For text output, print directly to stdout as before, or use logger if preferred
             if args.output_type == 'text':
                 print(response) # Keep print for direct output, or use logger.info(response)
             else:
                 # Handle non-saved image output if necessary (e.g., print confirmation)
                 logger.info("Image generated successfully (output not saved).")

    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True) # Log exception details
        # Optionally re-raise or exit
        # parser.exit(1)


if __name__ == '__main__':
    main()