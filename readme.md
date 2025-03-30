# README.md

# Gemini CLI

Gemini CLI is a command-line interface for interacting with the Gemini API. This tool allows users to provide text or file prompts, process various file types (images, text, PDFs, audio, video), and save outputs in different formats.

## Features

- Provide text or file prompts for API interaction
- Process multiple file types including images, text, PDFs, audio, and video
- Support for folder input with automatic file type detection
- Size validation for uploaded files (limited to 20MB)
- Save output to a specified file path
- Choose between text or image output types
- Select different models for generating responses

## Installation

To set up the project, follow these steps:

1.  **Clone the Repository:** First, ensure you have `git` installed on your system. Then, open your terminal and run the following commands:

    ```bash
    git clone https://github.com/yourusername/gemini-cli.git
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
gemini-cli -p "Your text prompt here" -i "path/to/your/file_or_folder" -f "*.jpg" -o "path/to/output/file" -t "text|image" -m "model_alias"
```

### Command-Line Options

-   `-p`, `--prompt`: Text prompt to send to the API. This can also be a file path containing the prompt text.
-   `-i`, `--input`: Path to an input file or folder. Supports various file formats including images, PDFs, text files, audio, and video.
-   `-f`, `--filter`: Filter pattern for files when `-i` points to a folder (e.g., `"*.txt"`, `"*.jpg"`).
-   `-o`, `--output`: Optional path where the output will be saved:
     - If omitted: Text outputs are only displayed on screen, non-text outputs are saved with auto-generated filenames
     - If `-o` with no value: Save with auto-generated filename
     - If `-o folder_path/`: Save file with auto-generated name in the specified directory
     - If `-o filename`: Save output to the specified filename
-   `-t`, `--output-type`: Specify the output type (`text` or `image`). If omitted, it's inferred from the selected model's default.
-   `-m`, `--model`: Select the model alias to use for generating responses (e.g., "default", "flash", "pro", "vision", "imagen"). See `MODEL_MAP` in [`gemini-cli/gemini_cli/cli.py`](gemini-cli/gemini_cli/cli.py) for available aliases.

### Supported File Formats

The CLI supports the following file formats (defined in [`gemini-cli/gemini_cli/utils.py`](gemini-cli/gemini_cli/utils.py)):

-   **Images**: png, jpg, jpeg, gif
-   **Text files**: txt, csv, json, xml, html, java, cpp, py
-   **PDF files**: pdf
-   **Video files**: mp4, avi, mov (experimental)
-   **Audio files**: mp3, wav, flac (experimental)

File size is limited to 20MB for all formats.

### Use Cases

-   Generate Text from a Prompt:

    ```bash
    gemini-cli -p "What is the capital of France?"
    gemini-cli -o "output.txt" -p "What is the capital of France?"
    gemini-cli -o "output.txt" -t "text" -m "default" -p "What is the capital of France?"
    ```

    **Note:** For long prompts, placing `-p` at the end of the command can improve readability and command parsing in some shells.

-   Generate Text from a Prompt File:

    ```bash
    gemini-cli -p ./prompts/test.txt -o output.txt
    gemini-cli -p ./resources/prompts/questions.txt -i ./resources/questions.txt 
    ```

    This reads the contents of `./prompts/test.txt` file and uses it as the prompt.

-   Process Images with Prompts:

    ```bash
    gemini-cli -i ./resources/diagram.png -p "Explain this diagram in detail"
    gemini-cli -i ./resources/flower-with-bees.jpeg -p "Identify the species of bee in this image" -o "bee-analysis.txt"
    gemini-cli -i ./resources -f "trx*.png" -p "summarize the transactions and return in md table" -o 
    ```

-   Analyze Text Files:

    ```bash
    gemini-cli -i ./resources/questions.txt -p "Answer these questions"
    ```

-   Process PDF Documents:

    ```bash
    # Assuming you have a PDF file at ./documents/report.pdf
    gemini-cli -i ./documents/report.pdf -p "Summarize this report" -o "summary.txt"
    ```

-   Process a Folder of Images:

    ```bash
    # Process all supported files in the resources folder
    gemini-cli -i ./resources/ -p "Describe each image" -o "image-descriptions.txt"

    # Process only PNG files in the resources folder
    gemini-cli -i ./resources/ -f "*.png" -p "Describe each PNG image" -o "png-descriptions.txt"
    ```

-   Generate Images from Text (using Imagen or Flash Image model):

    ```bash
    gemini-cli -p "Generate a photorealistic image of a futuristic city" -t image -m imagen -o generated-city.jpg
    gemini-cli -p "A watercolor painting of a cat wearing a hat" -t image -m flash-img -o cat-painting.jpg
    ```

-   Use Different Models:

    ```bash
    gemini-cli -p "Write a technical analysis of quantum computing" -m pro -o "analysis.txt"
    gemini-cli -i ./resources/diagram.png -p "Describe this image" -m vision
    ```

-   Summarize transactions from images in a folder and output in Markdown table format:

    Command:
    ````bash
    # Assuming transaction images are named trx*.png in ./resources
    gemini-cli -o hisaab.txt -f "trx*.png" -i ./resources  -p "summarize total transactions and return in md table format"
    ````

    Expected Output in `hisaab.txt`:
    ````text
    | Description | Amount |
    |---|---|
    | Sent Amount | $3739.73 |
    | Received Amount | ₹333,580.18 |
    | Exchange Rate | ₹89.20 |
    | Coupon Savings | ₹7778.64 |
    ````

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
python3 -m unittest gemini-cli/tests/test_gemini_api.py
python3 -m unittest gemini-cli/tests/test_cli.py
python3 -m unittest gemini-cli/tests/test_api_interface.py
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
