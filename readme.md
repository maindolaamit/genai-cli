# Gemini CLI

This project provides a command-line interface (CLI) for interacting with the Google Gemini API. It allows users to generate text, images, and potentially other content types using various Gemini models, process diverse input files, and manage output effectively.

## Features

*   **Multi-Model Support:** Supports multiple Gemini models (e.g., `flash`, `pro`, `imagen`). The supported models and their capabilities are defined in `MODEL_MAP` within `cli.py`. New models can be added easily.
*   **Multiple Model Execution:** Run the same prompt against multiple models simultaneously (e.g., `-m flash,pro`) to compare outputs. Outputs are saved automatically with distinct filenames.
*   **Multimodal Input:** Accepts text prompts, and input files (images, audio, video, PDF, text files, etc.) depending on the chosen model's capabilities. Supports single file or folder input.
*   **Input Filtering:** Allows filtering files within input folders using wildcard patterns (`-f`). Processes a limited number of files per run (default: 5).
*   **Flexible Output:**
    *   Generates text or image outputs as specified by `-t` or inferred from the model.
    *   **Text output:** Always printed to the console. Saved to a file *only* if `-o` is specified.
    *   **Image/Binary output:** Always saved to a file. An automatic filename is generated if `-o` is omitted or points to a directory.
    *   Automatic filename format: `<first-four-prompt-words>_<model_name>_<timestamp>.<ext>`.
*   **Image Preview (Optional):** If the `imgcat` utility is installed on your system, generated images will be automatically previewed in the terminal after saving.
*   **Automatic File API Usage:** Automatically uses the Google AI File API for input files exceeding size limits (currently 20MB), enabling processing of larger files.
*   **Prompt File Support:** Accepts a file path for the prompt via `-p`.
*   **Instructions File Support:** Accepts a file path for instructions via `-i` to guide the model.
*   **List Available Models:** Use `--list-models` to see available model aliases and their capabilities.
*   **Error Handling:** Includes comprehensive error handling and logging.
*   **Graceful Exit:** Handles `SIGINT` (Ctrl+C) and `SIGTERM` signals.

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url> # Replace with your repository URL
    cd genai-cli
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    # Or if installing the package directly (from the genai-cli directory):
    # cd gemini-cli
    # pip install .
    ```

4.  **Set your Gemini API key:** Set the `GEMINI_API_KEY` environment variable. Add this line to your shell config file (e.g., `~/.zshrc`, `~/.bashrc`):
    ```bash
    export GEMINI_API_KEY="YOUR_API_KEY"
    ```
    Remember to source the file (e.g., `source ~/.zshrc`) or restart your terminal.

5.  **Optional: Install `imgcat` for image preview:**
    *   **macOS (using Homebrew):**
        ```bash
        brew install imgcat
        ```
    *   **Other systems:** Refer to [iTerm2 Utilities](https://iterm2.com/utilities/imgcat) or search for `imgcat` installation instructions for your specific terminal/OS.

## Usage

**Basic Examples:**

```bash
# Generate text from a prompt and print to console
gemini-cli -p "Explain the difference between AI, ML, and DL."

# Generate text and save to a specific file
gemini-cli -p "Write a python function for bubble sort." -o bubble_sort.py

# Use instructions from a file, process an image, save text output
gemini-cli -i ./instructions.txt -a ./diagram.png -p "Describe this diagram based on the instructions." -m vision -o description.txt

# Generate an image and save it (auto-filename)
gemini-cli -p "A futuristic cityscape at dawn, watercolor style" -m imagen -t image -o

# Generate an image and save to a specific path
gemini-cli -p "A robot reading a book in a library" -m imagen -t image -o ./outputs/robot_reading.jpg

# Process all JPG files in a folder and summarize them
gemini-cli -a ./receipts/ -f "*.jpg" -p "Summarize the key items and totals from these receipts." -o summary.txt

# Compare outputs from two different models (files saved automatically)
gemini-cli -p "What is the airspeed velocity of an unladen swallow?" -m flash,pro -o
```

**List Available Models:**

```bash
gemini-cli --list-models
```

**Command-Line Options:**

*   `-p, --prompt`: The text prompt (or path to a prompt file). Required if `-a` is not used.
*   `-i, --instructions`: Optional path to a file containing additional instructions for the model, or the instructions text itself.
*   `-a, --input`: Path to an input file or folder. Required if `-p` is not used.
*   `-f, --filter`: Glob pattern to filter files when `-a` is a folder (e.g., `"*.jpg"`).
*   `-o, --output`: Path to save the output.
    *   If omitted for `text` output: Prints to console only.
    *   If omitted for `image`/binary output: Saves to an auto-generated filename in the current directory.
    *   If present with no value (e.g., `-o`): Saves to an auto-generated filename in the current directory.
    *   If a directory path (e.g., `-o ./results/`): Saves to an auto-generated filename in that directory.
    *   If a full file path (e.g., `-o report.txt`): Saves to that specific file.
*   `-t, --output-type`: The type of output (`text` or `image`). If omitted, defaults to the model's default output type.
*   `-m, --model`: Comma-separated list of Gemini model alias(es) to use (e.g., `flash`, `pro`, `flash,pro`). See `--list-models` for choices. Defaults to `default`.
*   `--list-models`: Action flag to list available models and exit.

**Note:** Image previews require `imgcat` to be installed and accessible in your PATH. Folder inputs process a maximum of 5 supported files by default.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.

## License

[Specify your license here, e.g., MIT License]
