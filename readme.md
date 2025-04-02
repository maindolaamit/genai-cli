```markdown
# Gemini CLI

This project provides a command-line interface (CLI) for interacting with the Google Gemini API.  It allows users to generate text, images, and potentially other content types using various Gemini models.

## Features

* **Multi-Model Support:**  Supports multiple Gemini models (e.g., `gemini-2.0-flash`, `gemini-2.5-pro`, `imagen`).  The supported models are defined in the `MODEL_MAP` within `cli.py`.  New models can be added easily.
* **Multimodal Input:** Accepts text prompts, and input files (images, audio, video, PDF, etc.) depending on the chosen model's capabilities.
* **Flexible Output:** Generates text, images, and other output types as supported by the selected model and specified using the `-t` flag.  Output is written to a file specified by `-o`, or printed to the console for text output if `-o` is not specified.
* **Input Filtering:** Allows filtering files within input folders using wildcard patterns (`-f`).
* **Error Handling:** Includes comprehensive error handling and logging for API requests and file processing.
* **Graceful Exit:** Handles `SIGINT` (Ctrl+C) and `SIGTERM` signals for clean termination.
* **Prompt File Support:** Accepts a file path for the prompt via `-p`.  The file's contents are used as the prompt.
* **Instructions File Support:** Accepts a file path for instructions via `-i`.  The file's contents are included as instructions for the model.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository_url>
   ```

2. **Create a virtual environment (recommended):**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set your Gemini API key:**  Set the `GEMINI_API_KEY` environment variable with your API key.  For example (Bash):
   ```bash
   export GEMINI_API_KEY="YOUR_API_KEY"
   ```


## Usage

```bash
gemini-cli -p "Write a short story about a robot learning to love." -o output.txt
gemini-cli -i "instructions.txt" -a input_image.jpg -m vision -o output.txt -t text
gemini-cli -p "Generate an image of a cat sitting on a mat" -m imagen -o output.jpg -t image
```

**Options:**

* `-p, --prompt`:  The text prompt (or path to a prompt file).
* `-i, --instructions`: The path to a file containing additional instructions for the model.
* `-a, --input`: Path to an input file or folder.
* `-f, --filter`: Filter for files in input folder (e.g., "*.jpg").
* `-o, --output`: Path to save the output (optional, defaults to console for text, auto-generated filename otherwise).  If specified as a directory, a filename will be automatically generated within that directory.
* `-t, --output-type`: The type of output ('text' or 'image'). If omitted, it defaults to the model's default output type.
* `-m, --model`: The Gemini model alias to use (see `MODEL_MAP` in `cli.py` for available aliases).  Defaults to "default", which typically maps to the `gemini-1.5-flash-latest` model.


## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

[Specify your license here, e.g., MIT License]
```
