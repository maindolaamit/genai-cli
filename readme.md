# README.md

# Gemini CLI

Gemini CLI is a command-line interface for interacting with the Gemini API. This tool allows users to provide text or file prompts, process various file types (images, text, PDFs, audio, video), and save outputs in different formats.

## Features

- Provide text or file prompts for API interaction
- Add optional instructions to guide the model's response
- Process multiple file types including images, text, PDFs, audio, and video
- Support for folder input with automatic file type detection and filtering
- Size validation for uploaded files (limited to 20MB, uses File API for larger files)
- Save output to a specified file path, with auto-filename generation
- Choose between text or image output types (more types planned)
- Select different models for generating responses using aliases
- Text output is always printed to console for convenience
- Non-text outputs are automatically saved to files

## Installation

To set up the project, follow these steps:

1.  **Clone the Repository:** First, ensure you have `git` installed on your system. Then, open your terminal and run the following commands:

    ```bash
    git clone https://github.com/yourusername/gemini-cli.git # Replace with the actual repo URL if different
    cd genai-cli # Navigate into the main project directory
    ```

2.  **Install the Package:** Make sure you have Python 3 and `pip3` installed. Navigate into the `gemini-cli` sub-directory and use `pip3` to install the package. This command reads the `setup.py` file and installs the CLI along with its dependencies.

    ```bash
    cd gemini-cli
    pip3 install .
    ```
    *   This will install the `gemini-cli` command to a location typically included in your system's PATH (like `~/.local/bin` on Linux/macOS).
    *   Ensure the installation directory (e.g., `~/.local/bin`) is in your `PATH` environment variable. If not, add it to your shell's configuration file (e.g., `~/.zshrc` or `~/.bashrc`) and source it (`source ~/.zshrc`).

3.  **Set Gemini API Key:** Obtain your Gemini API key and set it as an environment variable named `GEMINI_API_KEY`. Add the following line to your shell's configuration file (e.g., `~/.zshrc` or `~/.bashrc`), replacing `YOUR_GEMINI_API_KEY_HERE` with your actual key:

    ```bash
    export GEMINI_API_KEY='YOUR_GEMINI_API_KEY_HERE'
    ```
    *   After adding the key, restart your terminal or source your configuration file again (e.g., `source ~/.zshrc`).

## Usage

Once installed, you can use the `gemini-cli` command directly from your terminal:

```bash
gemini-cli -p "Your text prompt here" -i "Additional instructions" -a "path/to/your/file_or_folder" -f "*.jpg" -o "path/to/output/file" -t "text|image" -m "model_alias"
```

### Command-Line Options

-   `-p`, `--prompt`: Text prompt to send to the API. This can also be a file path containing the prompt text.
-   `-i`, `--instructions`: Additional instructions to guide the model. This can also be a file path containing the instructions text.
-   `-a`, `--input`: Path to an input file or folder to add context. Supports various file formats.
-   `-f`, `--filter`: Filter pattern for files when `-a` points to a folder (e.g., `"*.txt"`, `"*.jpg"`).
-   `-o`, `--output`: Optional path where the output will be saved:
     - If omitted for text output: Text is only displayed on the console.
     - If omitted for non-text output: Saved with an auto-generated filename in the current directory.
     - If `-o` with no value: Save with auto-generated filename in the current directory.
     - If `-o folder_path/`: Save file with auto-generated name in the specified directory.
     - If `-o filename`: Save output to the specified filename.
-   `-t`, `--output-type`: Specify the output type (`text` or `image`). If omitted, it's inferred from the selected model's default.
-   `-m`, `--model`: Select the model alias(es) to use, comma-separated (e.g., "flash", "pro", "imagen"). See `MODEL_MAP` in [`gemini-cli/gemini_cli/cli.py`](gemini-cli/gemini_cli/cli.py) for available aliases. Default: "default".

### Supported File Formats

The CLI supports the following file formats for input (defined in [`gemini-cli/gemini_cli/utils.py`](gemini-cli/gemini_cli/utils.py)):

-   **Images**: png, jpg, jpeg, gif
-   **Text files**: txt, csv, json, xml, html, java, cpp, py
-   **PDF files**: pdf
-   **Video files**: mp4, avi, mov (processed via File API)
-   **Audio files**: mp3, wav, flac (processed via File API or inline)

File size is limited to 20MB for inline processing. Larger files are automatically handled using the Google AI File API.

### Use Cases

-   Generate Text from a Prompt:

    ```bash
    # Simple text prompt
    gemini-cli -p "What is the capital of France?"

    # Save text output to a specific file
    gemini-cli -p "Explain quantum computing in simple terms." -o explanation.txt

    # Use instructions from a file
    gemini-cli -p "Summarize the main points of this article." -a ./resources/article.txt -i ./resources/instructions/out-md.txt -o summary.md
    ```

-   Generate Text from a Prompt File:

    ```bash
    # Use content of a file as the prompt
    gemini-cli -p ./resources/prompts/questions.txt -a ./resources/questions.txt -o formatted_notes.txt

    # Use a prompt file and provide instructions
    gemini-cli -p ./resources/prompts/city.txt -i "Make the tone more optimistic." -o city_description.txt
    ```

-   Process Images with Prompts:

    ```bash
    # Explain a diagram image
    gemini-cli -a ./resources/diagram.png -p "Explain this diagram in detail"

    # Identify something in an image and save the analysis
    gemini-cli -a ./resources/flower-with-bees.jpeg -p "Identify the species of bee in this image" -o "bee-analysis.txt"
    ```

-   Process Files in a Folder:

    ```bash
    # Summarize all PNG transaction images in a folder into a markdown table
    gemini-cli -a ./resources -f "trx*.png" -p "Summarize the transactions and return in markdown table" -o hisaab_summary.md

    # Describe all supported files in a folder
    gemini-cli -a ./resources/ -p "Describe each file briefly." -o folder_description.txt
    ```

-   Generate Images from Text:

    ```bash
    # Generate an image using the 'imagen' model alias
    gemini-cli -p "Generate a photorealistic image of a futuristic city at sunset" -t image -m imagen -o generated-city.jpg

    # Generate an image using the 'flash-img' model alias
    gemini-cli -p "A watercolor painting of a cat wearing a tiny hat" -t image -m flash-img -o cat-painting.jpg
    ```

-   Use Different Models:

    ```bash
    # Get a technical analysis using the 'pro' model
    gemini-cli -p "Write a technical analysis of the Llama 3 architecture" -m pro -o "llama3_analysis.txt"

    # Describe an image using the default 'vision' capable model
    gemini-cli -a ./resources/diagram.png -p "Describe this image" -m vision
    ```

-   Compare Outputs from Multiple Models:

    ```bash
    # Ask the same question to 'flash' and 'pro' models (outputs saved automatically)
    gemini-cli -p "What are the key differences between Python 2 and Python 3?" -m flash,pro -o
    # This will generate two files, e.g.:
    # what-are-the_gemini-2_0-flash_20250331-110000.txt
    # what-are-the_gemini-2_5-pro-exp-03-25_20250331-110001.txt
    ```

## Testing

This project includes a comprehensive test suite to ensure all components function correctly. The tests use Python's `unittest` framework with mocking to avoid actual API calls during testing.

### Test Files

The test suite consists of four main test files located in the `gemini-cli/tests` directory:

1.  **test_utils.py** - Tests for utility functions ([`gemini-cli/gemini_cli/utils.py`](gemini-cli/gemini_cli/utils.py)).
2.  **test_gemini_api.py** - Tests for the Gemini API client ([`gemini-cli/gemini_cli/gemini_api.py`](gemini-cli/gemini_cli/gemini_api.py)).
3.  **test_cli.py** - Tests for the command-line interface ([`gemini-cli/gemini_cli/cli.py`](gemini-cli/gemini_cli/cli.py)).
4.  **test_api_interface.py** - Tests for the API interface module ([`gemini-cli/gemini_cli/api_interface.py`](gemini-cli/gemini_cli/api_interface.py)).

### Running Tests

To run the entire test suite, use the following command from the **project root directory** (`genai-cli`):

```bash
python3 -m unittest discover -s gemini-cli/tests
```

To run a specific test file:

```bash
python3 -m unittest gemini-cli/tests/test_utils.py
# etc.
```

### Adding New Tests

When adding new features to the CLI, please ensure:

1.  Write tests for any new functionality in the appropriate test file.
2.  Use mocking (`unittest.mock`) for external dependencies like API calls or file system interactions where necessary.
3.  Run the test suite before submitting changes.
4.  Ensure existing tests continue to pass.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License.
