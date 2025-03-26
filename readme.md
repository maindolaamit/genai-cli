# README.md

# Gemini CLI

Gemini CLI is a command-line interface for interacting with the Gemini API. This tool allows users to provide text or file prompts, attach files, specify additional context through folder paths, and save outputs in various formats.

## Features

- Provide text or file prompts for API interaction.
- Attach files via command-line parameters.
- Specify a folder path for additional context.
- Save output to a specified file path.
- Choose between text or image output types.
- Select different models for generating responses.

## Installation

To set up the project, follow these steps:

1.  **Clone the Repository:** First, ensure you have `git` and `pip` installed on your system. Then, open your terminal and run the following commands to
    ```bash
    git clone https://github.com/yourusername/gemini-cli.git
    cd gemini-cli
    pip install -r requirements.txt
    ```

2.  **Install Dependencies:** Navigate to the cloned directory and install the required Python packages using `pip`. This will install all necessary dependencies listed in `requirements.txt`.
    ```bash
    cd gemini-cli
    pip3 install -r requirements.txt
    ```

3.  **Make the Script Executable:** Grant execute permissions to the script:

    ```bash
    chmod +x gemini-cli/src/cli.py
    ```

4.  **Create a Symbolic Link:** Create a symbolic link in `~/.local/bin` to make the script accessible from your `PATH`. Ensure `~/.local/bin` is in your `PATH` environment variable (usually it is by default on macOS).

    ```bash
    ln -s $(pwd)/gemini-cli/src/cli.py ~/.local/bin/gemini-cli
    ```

5.  **Create command in ~/.local/bin:** If you want to run the command from anywhere, create a command in `~/.local/bin`:

    ```bash
    echo 'alias gemini-cli="python ~/.local/bin/cli.py"' >> ~/.zshrc
    ```

    Then, source your `.zshrc` file to apply the changes:

    ```bash
    source ~/.zshrc
    ```

6.  **Set Gemini API Key:** Obtain your Gemini API key and set it as an environment variable as `GEMINI_API_KEY` in your `.zshrc` file (or your shell's configuration file, e.g., `.bash_profile`, `.bashrc` if you are using bash).

    Open your `.zshrc` file in a text editor:

    ```bash
    nano ~/.zshrc
    ```

    Add the following line, replacing `YOUR_GEMINI_API_KEY_HERE` with your actual API key:

    ```bash
    export GEMINI_API_KEY='YOUR_GEMINI_API_KEY_HERE'
    ```

## Usage

To use the Script, run the following command:
```bash
python gemini-cli/src/cli.py -p "Your text prompt here"
```

To use the CLI, run the following command:

```bash
gemini-cli -p "Your text prompt here" -f "path/to/your/file" -d "path/to/context/folder" -o "path/to/output/file" -t "text|image" -m "model_code"
```

### Command-Line Options

- `-p`, `--prompt`: Text prompt to send to the API.
- `-f`, `--file`: Path to a file to attach.
- `-d`, `--folder`: Path to a folder containing additional context files.
- `-o`, `--output`: Path where the output will be saved.
- `-t`, `--output-type`: Specify the output type (`text` or `image`).
- `-m`, `--model`: Select the model to use for generating responses.


### Use Cases
- Generate Text from a Prompt:
    ```bash
    gemini-cli "What is the capital of France?" 
    gemini-cli -p "What is the capital of France?" 
    gemini-cli -p "What is the capital of France?" -o "output.txt"
    gemini-cli -p "What is the capital of France?" -o "output.txt" -t "text" -m "text-advanced-model"
    ```

- Generate Text from a Prompt File and Save to Output File:
    ```bash
    genai -f prompt.txt --output-file story.txt
    gemini-cli -p "$(cat prompt.txt)" -o "output.txt" 
    ```
    (Assuming you have a file named prompt.txt with your prompt.)

- Describe Images:
    ```bash
    genai -p "Describe these images in detail." -i image1.jpg image2.png
    genai -p "Describe these images in detail." -i image1.jpg image2.png -o "output.txt"
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

When adding new features to the CLI, please ensure:

1. Write tests for any new functionality
2. Use mocking for external dependencies
3. Run the test suite before submitting a pull request
4. Ensure existing tests continue to pass

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.

## License

This project is licensed under the MIT License. See the LICENSE file for details.
