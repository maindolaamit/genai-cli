import logging
import os
import pathlib

# File formats supported by the CLI
FILE_FORMATS = {
    "image": ["png", "jpg", "jpeg", "gif"],
    "text": ["txt", "csv", ".tsv", "json", "xml", "html", "css", "md", "java", "cpp", "py", "rft", "sql", "yaml", "yml"],
    "pdf": ["pdf"],
    "doc": [".doc", "docx", ".pptx", ".ppt",".xls", "xlsx"],
    "video": ["mp4", "avi", "mov"],
    "audio": ["mp3", "wav", "flac"]
}

# Maximum file size in MB
MAX_FILE_SIZE = 20  # MB

# Add a dictionary for common document MIME types
DOC_MIME_TYPES = {
    '.doc': 'application/msword',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.xls': 'application/vnd.ms-excel',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.ppt': 'application/vnd.ms-powerpoint',
    '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    '.odt': 'application/vnd.oasis.opendocument.text', # Added ODT as an example
    # Add other document types as needed
}


def read_file(file_path):
    """Read the contents of a file and return them as a string."""
    with open(file_path, 'r') as file:
        return file.read()


def validate_file_path(file_path):
    """Check if the provided file path exists and is a file."""
    import os
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"The file at {file_path} does not exist.")


def validate_folder_path(folder_path):
    """Check if the provided folder path exists and is a directory."""
    import os
    if not os.path.isdir(folder_path):
        raise NotADirectoryError(f"The folder at {folder_path} does not exist.")


def load_environment_variable(var_name):
    """Load an environment variable and return its value."""
    import os
    value = os.getenv(var_name)
    if value is None:
        raise EnvironmentError(f"The environment variable {var_name} is not set.")
    return value


def process_image(image_path):
    """Process an image file and convert it to base64 for the Gemini API."""
    from PIL import Image

    # Validate file exists and is within size limits
    validate_file_path(image_path)
    validate_file_size(image_path)
    # Open and process the image
    return Image.open(image_path)


def process_doc(file_path):
    """
    Reads a document file and determines its MIME type.

    Args:
        file_path (str): Path to the document file.

    Returns:
        tuple: (bytes, str) - The file content as bytes and the determined MIME type.
               Returns (None, None) if MIME type cannot be determined.
    """
    logger = setup_logger("utils")
    try:
        # Read the file content as bytes
        with open(file_path, 'rb') as f:
            doc_data = f.read()

        # Determine MIME type from extension
        _, ext = os.path.splitext(file_path)
        mime_type = DOC_MIME_TYPES.get(ext.lower())

        if not mime_type:
            logger.warning(f"Could not determine MIME type for document extension: {ext}")
            # Default or raise error? For now, returning None.
            # Consider a default like 'application/octet-stream' if needed.
            return doc_data, None # Or raise ValueError

        logger.info(f"Processed document '{os.path.basename(file_path)}' with MIME type: {mime_type}")
        return doc_data, mime_type

    except FileNotFoundError:
        logger.error(f"Document file not found: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Error processing document file {file_path}: {e}")
        raise


def process_pdf(pdf_path):
    """
    Process a PDF file for the Gemini API.
    
    Args:
        pdf_path (str): Path to the PDF file.
    
    Returns:
        bytes: Processed PDF data
    """
    # Validate file exists and is within size limits
    validate_file_path(pdf_path)
    validate_file_size(pdf_path)

    # Read the PDF file and return bytes
    with open(pdf_path, 'rb') as file:
        pdf_data = file.read()

    return pdf_data


def process_text_file(text_path):
    """
    Process a text file for the Gemini API.
    
    Args:
        text_path (str): Path to the text file.
    
    Returns:
        str: Text content
    """
    # Validate file exists and is within size limits
    validate_file_path(text_path)
    validate_file_size(text_path)

    # Read the text file
    with open(text_path, 'r', encoding='utf-8', errors='replace') as file:
        text_data = file.read()

    return text_data


def process_audio(audio_path):
    """
    Process an audio file for the Gemini API.
    
    Args:
        audio_path (str): Path to the audio file.
    
    Returns:
        bytes: Processed audio data
    """
    # Validate file exists and is within size limits
    validate_file_path(audio_path)
    validate_file_size(audio_path)

    # Read the audio file as binary
    with open(audio_path, 'rb') as file:
        audio_data = file.read()

    return audio_data


def process_video(video_path):
    """
    Process a video file for the Gemini API.
    
    Args:
        video_path (str): Path to the video file.
    
    Returns:
        bytes: Processed video data
    """
    # Validate file exists and is within size limits
    validate_file_path(video_path)
    validate_file_size(video_path)

    # Read the video file as binary
    with open(video_path, 'rb') as file:
        video_data = file.read()

    return video_data


def get_file_type(file_path):
    """
    Determine the type of file based on its extension.
    
    Args:
        file_path (str): Path to the file.
    
    Returns:
        str: File type ('image', 'text', 'pdf', 'video', 'audio') or None if not supported.
    """
    extension = pathlib.Path(file_path).suffix.lower().lstrip('.')

    for file_type, extensions in FILE_FORMATS.items():
        if extension in extensions:
            return file_type

    return None


def is_validate_file_size(file_path):
    """
    Check if the file size is within the allowed limit.

    Args:
        file_path (str): Path to the file.

    Raises:
        ValueError: If the file exceeds the maximum size limit.
    """
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)  # Convert to MB

    return file_size_mb < MAX_FILE_SIZE


def validate_file_size(file_path):
    """
    Check if the file size is within the allowed limit.
    
    Args:
        file_path (str): Path to the file.
    
    Raises:
        ValueError: If the file exceeds the maximum size limit.
    """
    file_size_bytes = os.path.getsize(file_path)
    file_size_mb = file_size_bytes / (1024 * 1024)  # Convert to MB

    if file_size_mb > MAX_FILE_SIZE:
        raise ValueError(f"File size ({file_size_mb:.2f} MB) exceeds the maximum limit of {MAX_FILE_SIZE} MB.")


def get_files_from_folder(folder_path, file_filter=None):
    """
    Get list of files from a folder, optionally filtered by type or pattern.
    
    Args:
        folder_path (str): Path to the folder.
        file_filter (str, optional): Filter pattern for files (e.g., '*.jpg').
    
    Returns:
        list: List of file paths that match the filter criteria.
    """
    import glob
    import os

    # Check if folder is empty
    if not os.listdir(folder_path):
        logger = setup_logger()
        logger.warning(f"The folder at {folder_path} is empty.")
        return []

    # If filter is provided, use it to find matching files
    if file_filter:
        # Handle wildcards in filter pattern
        pattern = os.path.join(folder_path, file_filter)
        matching_files = glob.glob(pattern)
        return [f for f in matching_files if os.path.isfile(f)]

    # Otherwise, get all files with supported extensions
    result = []
    supported_extensions = []
    for extensions in FILE_FORMATS.values():
        supported_extensions.extend(extensions)

    for root, _, files in os.walk(folder_path):
        for file in files:
            file_path = os.path.join(root, file)
            extension = pathlib.Path(file_path).suffix.lower().lstrip('.')
            if extension in supported_extensions:
                result.append(file_path)

    return result


def validate_file_type(file_path, supported_types=None):
    """
    Validate if the file type is supported.
    
    Args:
        file_path (str): Path to the file.
        supported_types (list, optional): List of supported file types.
                                         If None, validates against all FILE_FORMATS.
    
    Returns:
        str: The file type if valid.
    
    Raises:
        ValueError: If the file type is not supported.
    """
    file_type = get_file_type(file_path)

    if file_type is None:
        extension = pathlib.Path(file_path).suffix.lower()
        raise ValueError(f"File type {extension} is not supported.")

    if supported_types and file_type not in supported_types:
        raise ValueError(f"File type {file_type} is not supported for this operation.")

    return file_type


# --- Colored Logging Setup ---

class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log levels."""
    grey = "\x1b[38;20m"
    blue = "\x1b[34;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"

    # Define format string including level name and message
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

    FORMATS = {
        logging.DEBUG: grey + log_format + reset,
        logging.INFO: blue + log_format + reset,
        logging.WARNING: yellow + log_format + reset,
        logging.ERROR: red + log_format + reset,
        logging.CRITICAL: bold_red + log_format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logger(name='gemini_cli', level=logging.INFO):
    """Sets up and returns a logger with colored output."""
    logger = logging.getLogger(name)

    # Prevent adding multiple handlers if logger already exists
    if logger.hasHandlers():
        logger.handlers.clear()

    logger.setLevel(level)

    # Create console handler with colored formatter
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(ColoredFormatter())

    logger.addHandler(ch)
    return logger

# --- End Colored Logging Setup ---
