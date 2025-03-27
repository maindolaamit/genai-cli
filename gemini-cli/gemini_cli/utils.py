import os
import logging

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
    import base64
    from PIL import Image
    import io
    
    # Open and process the image
    with Image.open(image_path) as img:
        # Convert to RGB if it's not already (e.g., if it's RGBA)
        if img.mode != "RGB":
            img = img.convert("RGB")
        
        # Resize image if needed
        # img = img.resize((800, 800))  # Optional resize
        
        # Convert to bytes
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        image_bytes = buffer.getvalue()
        
        # Encode to base64
        base64_encoded = base64.b64encode(image_bytes).decode("utf-8")
        
        return base64_encoded

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