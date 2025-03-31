import os
import tempfile
from typing import Dict, List, Any, Union, Optional

from PIL import Image
import google.generativeai as genai

from .utils import (
    validate_file_path,
    setup_logger,
    is_validate_file_size,
    process_image,
    process_text_file,
    process_pdf,
    process_audio,
    process_video
)

# Initialize the logger
logger = setup_logger()

class GeminiAPI:
    """
    Client for the Gemini API that handles various types of content generation.
    """
    
    def __init__(self):
        """Initialize the Gemini API client with the API key from environment."""
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables.")
        
        genai.configure(api_key=api_key)
        
        # Keep track of uploaded files for cleanup
        self._uploaded_files = []
    
    @property
    def uploaded_files(self) -> List[str]:
        """Return a list of file names that have been uploaded."""
        return self._uploaded_files
    
    def delete_uploaded_files(self):
        """Delete all uploaded files."""
        for file_name in self._uploaded_files:
            try:
                genai.delete_file(file_name)
                logger.info(f"Deleted uploaded file: {file_name}")
            except Exception as e:
                logger.warning(f"Failed to delete file {file_name}: {e}")
        
        self._uploaded_files = []
    
    def get_processed_file_content(self, file_path: str, file_type: str) -> Any:
        """
        Process a file based on its type and return content ready for the API.
        
        Args:
            file_path (str): Path to the file.
            file_type (str): Type of the file (image, text, pdf, audio, video).
            
        Returns:
            Any: Processed content ready for the API.
        """
        validate_file_path(file_path)
        
        # Check if file is too large (>20MB) for direct upload
        use_file_api = not is_validate_file_size(file_path)
        
        if use_file_api:
            # File is too large, use File API
            logger.info(f"File {file_path} is large, using File API")
            try:
                uploaded_file = genai.upload_file(path=file_path)
                self._uploaded_files.append(uploaded_file.name)
                return uploaded_file
            except Exception as e:
                logger.error(f"Failed to upload file {file_path}: {e}")
                raise
        
        # Process file based on its type
        try:
            if file_type == 'image':
                return process_image(file_path)
            elif file_type == 'text':
                return process_text_file(file_path)
            elif file_type == 'pdf':
                return process_pdf(file_path)
            elif file_type == 'audio':
                return process_audio(file_path)
            elif file_type == 'video':
                return process_video(file_path)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            raise
    
    def generate_text_content(self, prompt_text: str, model: str) -> str:
        """
        Generate text content from a text prompt.
        
        Args:
            prompt_text (str): The text prompt.
            model (str): The model to use.
            
        Returns:
            str: The generated text content.
        """
        try:
            # Initialize the generative model
            model_client = genai.GenerativeModel(model)
            
            # Prepare the contents
            contents = [prompt_text]
            
            # Generate content
            response = model_client.generate_content(contents=contents)
            
            return response.text
        except Exception as e:
            raise Exception(f"Error generating text content with model '{model}': {e}") from e
    
    def generate_image_content(self, prompt_text: str, model: str) -> bytes:
        """
        Generate image content from a text prompt.
        
        Args:
            prompt_text (str): The text prompt.
            model (str): The model to use.
            
        Returns:
            bytes: The generated image content.
        """
        try:
            # Initialize the generative model
            model_client = genai.GenerativeModel(model)
            
            # Create generation config for image output
            gen_config = genai.GenerationConfig(
                response_mime_type='image/jpeg',
            )
            
            # Generate content
            response = model_client.generate_content(
                contents=prompt_text,
                generation_config=gen_config
            )
            
            # Extract image data or text response
            if response.parts:
                for part in response.parts:
                    if hasattr(part, 'data') and part.data:
                        return part.data
                
                # If we get here, we didn't find image data but there were response parts
                logger.warning("No image data found in response")
                text_response = "".join([part.text for part in response.parts if hasattr(part, 'text')])
                return text_response
            
            # Fallback to response.text if no parts found
            if hasattr(response, 'text') and response.text:
                return response.text
            
            raise ValueError("No content returned from the model")
        except Exception as e:
            raise Exception(f"Error generating image content with model '{model}': {e}") from e
    
    def send_file_prompt(self, file_path: str, model: str, prompt_text: Optional[str] = None) -> Union[str, bytes]:
        """
        Sends the content of a file as a prompt to the Gemini model.
        
        Args:
            file_path (str): Path to the file to use as input.
            model (str): The model to use.
            prompt_text (str, optional): Additional text prompt to accompany the file.
            
        Returns:
            Union[str, bytes]: The response from the model, either text or binary data.
        """
        try:
            if file_path.endswith((".txt", ".csv", ".json", ".xml", ".html", ".java", ".cpp", ".py")):
                # Handle text files
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    text_content = f.read()
                
                # Combine with prompt_text if provided
                if prompt_text:
                    full_prompt = f"{prompt_text}\n\nContent from {os.path.basename(file_path)}:\n{text_content}"
                else:
                    full_prompt = text_content
                
                return self.generate_text_content(full_prompt, model)
            elif file_path.endswith((".png", ".jpg", ".jpeg", ".gif")):
                # Handle images
                image = Image.open(file_path)
                
                # Create model instance
                model_client = genai.GenerativeModel(model)
                
                # Prepare contents
                contents = []
                if prompt_text:
                    contents.append(prompt_text)
                contents.append(image)
                
                # Generate content
                response = model_client.generate_content(contents=contents)
                
                return response.text
            elif file_path.endswith((".pdf")):
                # Handle PDF files (simplified for now)
                if prompt_text:
                    logger.info(f"Processing PDF file with prompt: {prompt_text}")
                else:
                    logger.info("Processing PDF file with no additional prompt")
                
                # Implementation for PDF processing would go here
                # For now, return a placeholder
                return "PDF processing is not fully implemented yet."
            else:
                # Unsupported file type
                raise ValueError(f"Unsupported file type: {file_path}")
        except Exception as e:
            raise Exception(f"Error sending file prompt to Gemini model '{model}': {e}") from e
    
    def _send_prompt_with_image(self, image: Image.Image, model: str, prompt_text: Optional[str] = None) -> str:
        """
        Sends an image with optional text prompt to the Gemini model.
        
        Args:
            image (Image.Image): The image to send.
            model (str): The model to use.
            prompt_text (str, optional): Optional text prompt to accompany the image.
            
        Returns:
            str: The text response from the model.
        """
        try:
            # Create model instance
            model_client = genai.GenerativeModel(model)
            
            # Prepare contents
            contents = []
            if prompt_text:
                contents.append(prompt_text)
            contents.append(image)
            
            # Generate content
            response = model_client.generate_content(contents=contents)
            
            return response.text
        except Exception as e:
            raise Exception(f"Error sending image prompt to Gemini model '{model}': {e}") from e
    
    def generate_audio_content(self, prompt_text: str, model: str) -> bytes:
        """
        Generate audio content from a text prompt (placeholder for future implementation).
        
        Args:
            prompt_text (str): The text prompt.
            model (str): The model to use.
            
        Returns:
            bytes: The generated audio content.
        """
        # This is just a placeholder for now
        logger.warning("Audio generation is not yet implemented")
        raise NotImplementedError("Audio generation is not yet implemented")
    
    def generate_video_content(self, prompt_text: str, model: str) -> bytes:
        """
        Generate video content from a text prompt (placeholder for future implementation).
        
        Args:
            prompt_text (str): The text prompt.
            model (str): The model to use.
            
        Returns:
            bytes: The generated video content.
        """
        # This is just a placeholder for now
        logger.warning("Video generation is not yet implemented")
        raise NotImplementedError("Video generation is not yet implemented")
