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