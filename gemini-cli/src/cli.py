import argparse
import os
from api_interface import interact_with_gemini_api

MODEL_MAP = {
    "default": "gemini-1.5-pro-latest",
    "flash": "gemini-2.0-flash",
    "pro": "gemini-1.5-pro",
    "vision": "gemini-pro-vision",
    "imagen": "gemini-1.5-flash",
    "unknown-model": "gemini-unknown"
}

DEFAULT_TEXT_MODEL = "flash"
DEFAULT_IMAGE_MODEL = "vision"

def main():
    parser = argparse.ArgumentParser(description='Interact with the Gemini API.')

    required = parser.add_argument_group('required arguments')
    required.add_argument('-p', '--prompt', type=str, help='Text prompt to send to the API.')

    parser.add_argument('-f', '--file', type=str, help='Path to a file to send to the API.')
    parser.add_argument('-d', '--folder', type=str, help='Path to a folder for additional context.')
    parser.add_argument('-o', '--output', type=str, help='Path to save the output file.')
    parser.add_argument('-t', '--output-type', choices=['text', 'image'], default='text', help='Type of output to generate.')
    parser.add_argument('-m', '--model', type=str, default=None, help='Model code to use for the API request.')

    args = parser.parse_args()

    if not args.prompt and not args.file:
        parser.error('At least one of --prompt or --file must be provided.')

    if args.folder and not os.path.isdir(args.folder):
        parser.error('The specified folder path does not exist.')

    if args.file and not os.path.isfile(args.file):
        parser.error('The specified file path does not exist.')

    # Determine model based on output type and user input
    if args.model:
        model_name = MODEL_MAP.get(args.model)
        if not model_name:
            parser.error(f"Model code '{args.model}' not recognized. Valid model codes are: {', '.join(MODEL_MAP.keys())}")
    else:
        model_name = MODEL_MAP.get(DEFAULT_TEXT_MODEL if args.output_type == 'text' else DEFAULT_IMAGE_MODEL)

    if not model_name:
        model_name = MODEL_MAP["default"] # Fallback to default if no default is set for output type

    response = interact_with_gemini_api(args.prompt, args.file, args.folder, args.output_type, model_name)

    if args.output:
        with open(args.output, 'wb' if args.output_type == 'image' else 'w') as f:
            f.write(response)

if __name__ == '__main__':
    main()