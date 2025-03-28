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

1. **Clone the Repository:** First, ensure you have `git` installed on your system. Then, open your terminal and run the following commands:

    ```bash
    git clone https://github.com/yourusername/gemini-cli.git
    cd genai-cli # Navigate into the main project directory
    ```

2. **Install Dependencies:** Make sure you have Python 3 installed on your system. Use pip3 to install the required packages:

    ```bash
    cd gemini-cli
    pip3 install -r requirements.txt
    ```

3. **Run the Installation Script:** Navigate into the `gemini-cli` sub-directory and run the installation script. This will set permissions and create necessary links/aliases.

    ```bash
    chmod +x install.sh
    ./install.sh
    ```
    *   The script will create a log file named `installation.log`.
    *   It attempts to add an alias to your `~/.zshrc` file and source it. If you use a different shell (like bash), you might need to manually add the alias `alias gemini-cli="python3 ~/.local/bin/gemini-cli"` to your respective configuration file (e.g., `~/.bashrc`) and source it (`source ~/.bashrc`).
    *   Ensure `~/.local/bin` is in your `PATH` environment variable.

4. **Set Gemini API Key:** Obtain your Gemini API key and set it as an environment variable named `GEMINI_API_KEY`. Add the following line to your shell's configuration file (e.g., `~/.zshrc` or `~/.bashrc`), replacing `YOUR_GEMINI_API_KEY_HERE` with your actual key:

    ```bash
    export GEMINI_API_KEY='YOUR_GEMINI_API_KEY_HERE'
    ```
    *   After adding the key, restart your terminal or source your configuration file again (e.g., `source ~/.zshrc`).

## Usage

To use the script directly, run the following command:

```bash
python3 gemini-cli/src/cli.py -p "Your text prompt here"
```

To use the CLI with the installed alias, run the following command:

```bash
gemini-cli -p "Your text prompt here" -f "path/to/your/file" -d "path/to/context/folder" -o "path/to/output/file" -t "text|image" -m "model_code"
```

### Command-Line Options

- `-p`, `--prompt`: Text prompt to send to the API. This can also be a file path containing the prompt text.
- `-i`, `--input`: Path to an input file or folder. Supports various file formats including images, PDFs, text files, audio, and video.
- `-o`, `--output`: Path where the output will be saved.
- `-t`, `--output-type`: Specify the output type (`text` or `image`).
- `-m`, `--model`: Select the model to use for generating responses. Example values: "default", "flash", "vision", "imagen".

### Supported File Formats

The CLI supports the following file formats:

- **Images**: png, jpg, jpeg, gif
- **Text files**: txt, csv, json, xml, html, java, cpp, py
- **PDF files**: pdf
- **Video files**: mp4, avi, mov (experimental)
- **Audio files**: mp3, wav, flac (experimental)

File size is limited to 20MB for all formats.

### Use Cases

- Generate Text from a Prompt:

    ```bash
    gemini-cli -p "What is the capital of France?"
    gemini-cli -o "output.txt" -p "What is the capital of France?"
    gemini-cli -o "output.txt" -t "text" -m "default" -p "What is the capital of France?"
    ```

    **Note:** For long prompts, placing `-p` at the end of the command can improve readability and command parsing in some shells.

- Generate Text from a Prompt File:

    ```bash
    gemini-cli -p ./prompts/test.txt -o output.txt
    ```

    This reads the contents of `./prompts/test.txt` file and uses it as the prompt.

- Process Images with Prompts:

    ```bash
    gemini-cli -i ./resources/diagram.png -p "Explain this diagram in detail"
    gemini-cli -i ./resources/flower-with-bees.jpeg -p "Identify the species of bee in this image" -o "bee-analysis.txt"
    ```

- Analyze Text Files:

    ```bash
    gemini-cli -i ./resources/questions.txt -p "Answer these questions"
    ```

- Process PDF Documents:

    ```bash
    gemini-cli -i ./documents/report.pdf -p "Summarize this report" -o "summary.txt"
    ```

- Process a Folder of Images:

    ```bash
    gemini-cli -i ./resources/ -p "Describe each image" -o "image-descriptions.txt"
    ```

    This processes all supported image files in the resources folder.

- Generate Images from Text (using Imagen model):

    ```bash
    gemini-cli -p "Generate a photorealistic image of a futuristic city" -t image -m imagen -o generated-city.png
    ```

- Use Different Models:

    ```bash
    gemini-cli -p "Write a technical analysis of quantum computing" -m flash -o "analysis.txt"
    gemini-cli -i ./resources/robot.jpeg -p "Describe this image" -m vision
    ```

- Summarize transactions from images in a folder and output in Markdown table format:

    Command:
    ````bash
    gemini-cli -o hisaab.txt -f "trx*.png" -i ./resources  -p "summarize total transactions and retun in md table format"
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

The test suite consists of four main test files:

1. **test_utils.py** - Tests for utility functions:
   - Testing file reading and validation
   - Testing folder path validation
   - Testing environment variable loading
   - Testing image processing

2. **test_gemini_api.py** - Tests for the Gemini API client:
   - Testing API header construction
   - Testing text prompt requests (success and failure)
   - Testing file prompt handling
   - Testing response handling and output saving

3. **test_cli.py** - Tests for the command-line interface:
   - Testing command-line argument parsing
   - Testing model selection logic
   - Testing error handling scenarios

4. **test_api_interface.py** - Tests for the API interface module:
   - Testing text and file prompt handling
   - Testing folder context integration
   - Testing image output generation
   - Testing error conditions

### Running Tests

To run the entire test suite, use the following command from the project root:

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

1. Write tests for any new functionality
2. Use mocking for external dependencies
3. Run the test suite before submitting a pull request
4. Ensure existing tests continue to pass

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
