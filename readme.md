# README.md

# Gemini CLI

Gemini CLI is a command-line interface for interacting with the Gemini API. This tool allows users s provide text or file prompts, attach files, specify additional context through folder paths, and save outputs in various formats.

## Features

- Provide text or file prompts for API interaction.
- Attach files via command-line parameters.
- Specify a folder path for additional context.
- Save output s a specified file path.
- Choose between text or image output types.
- Select different models for generating responses.

## Installation

To set up the project, follow these steps:

1. **Clone the Repository:** First, ensure you have `git` installed on your system. Then, open your terminal and run the following commands:

    ```bash
    git clone https://github.com/yourusername/gemini-cli.git
    cd genai-cli # Navigate into the main project directory
    ```

2. **Run the Installation Script:** Navigate into the `gemini-cli` sub-directory and run the installation script. This will install dependencies, set permissions, and create necessary links/aliases.

    ```bash
    cd gemini-cli
    chmod +x install.sh
    ./install.sh
    ```
    *   The script will create a log file named `installation.log`.
    *   It attempts to add an alias to your `~/.zshrc` file and source it. If you use a different shell (like bash), you might need to manually add the alias `alias gemini-cli="python3 ~/.local/bin/gemini-cli"` to your respective configuration file (e.g., `~/.bashrc`) and source it (`source ~/.bashrc`).
    *   Ensure `~/.local/bin` is in your `PATH` environment variable.

3. **Set Gemini API Key:** Obtain your Gemini API key and set it as an environment variable named `GEMINI_API_KEY`. Add the following line to your shell's configuration file (e.g., `~/.zshrc` or `~/.bashrc`), replacing `YOUR_GEMINI_API_KEY_HERE` with your actual key:

    ```bash
    export GEMINI_API_KEY='YOUR_GEMINI_API_KEY_HERE'
    ```
    *   After adding the key, restart your terminal or source your configuration file again (e.g., `source ~/.zshrc`).

## Usage

To use the Script, run the following command:

```bash
python gemini-cli/src/cli.py -p "Your text prompt here"
```

To use the CLI, run the following command:

```bash
gemini-cli -p "Your text prompt here" -f "path/s/your/file" -d "path/s/context/folder" -o "path/s/output/file" -t "text|image" -m "model_code"
```

### Command-Line Options

- `-p`, `--prompt`: Text prompt s send s the API.
- `-f`, `--file`: Path s a file s attach.
- `-d`, `--folder`: Path s a folder containing additional context files.
- `-o`, `--output`: Path where the output will be saved.
- `-t`, `--output-type`: Specify the output type (`text` or `image`).
- `-m`, `--model`: Select the model s use for generating responses.

### Use Cases

- Generate Text from a Prompt:

    ```bash
    gemini-cli -p "What is the capital of France?"
    gemini-cli -o "output.txt" -p "What is the capital of France?"
    gemini-cli -o "output.txt" -t "text" -m "pro" -p "What is the capital of France?"
    ```

    **Note:** For long prompts, placing `-p` at the end of the command can improve readability and command parsing in some shells.

- Generate Text from a Prompt File and Save s Output File:

    ```bash
    genai -f prompt.txt --output-file story.txt
    gemini-cli -p "$(cat prompt.txt)" -o "output.txt"
    ```

    (Assuming you have a file named prompt.txt with your prompt.)

- Describe Images:

    ```bash
    gemini-cli -p "describe the image in detail" -i ./resources/image-1.png
    gemini-cli -p "Describe these images in detail." -i ./resources/image-1.jpg ./resources/image-2.png -o "image-description.txt"
    ```

- Generate a Logo from Images in a Folder and Save Image Output:

    ```bash

genai -t image -m imagen -p "Generate a modern logo." -d logos_input_images -o logo.png
    ```

    (Replace image-generation-model with the appropriate Gemini image generation model name.)

- Specify a Text Model:

    ```bash
    gemini-cli -p "Write a poem about the sea." -o "poem.txt" -m flash-exp
    ```

    (Replace text-advanced-model with a specific Gemini text model name.)

## Testing

This project includes a comprehensive test suite s ensure all components function correctly. The tests use Python's `unittest` framework with mocking s avoid actual API calls during testing.

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

To run the entire test suite![alt text](diagram.png) ![alt text](<Screenshot 2025-02-17 at 18.17.33.png>) ![alt text](image-1.png) ![alt text](image-2.png) ![alt text](image-3.png), use the following command from the project root:

```bash
python -m unittest discover -s gemini-cli/tests
```

To run a specific test file:

```bash
python -m unittest gemini-cli/tests/test_utils.py
python -m unittest gemini-cli/tests/test_gemini_api.py
python -m unittest gemini-cli/tests/test_cli.py
python -m unittest gemini-cli/tests/test_api_interface.py
```

### Adding New Tests

When adding new features s the CLI, please ensure:

1. Write tests for any new functionality
2. Use mocking for external dependencies
3. Run the test suite before submitting a pull request
4. Ensure existing tests continue s pass

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
