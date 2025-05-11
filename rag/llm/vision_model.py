from typing import Optional, Dict, Any
from PIL import Image
import base64
from io import BytesIO
import os
from litellm import completion

class VisionModel:
    """A vision model that uses OpenAI's GPT-4 Vision to describe images via litellm."""
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model_name: str = "gpt-4.1-mini",
        max_tokens: int = 500,
        temperature: float = 0.7
    ):
        """Initialize the vision model.
        
        Args:
            api_key: OpenAI API key. If not provided, will use OPENAI_API_KEY env var
            model_name: Name of the OpenAI model to use
            max_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (0-1)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key must be provided or set in OPENAI_API_KEY environment variable")
        
        os.environ["OPENAI_API_KEY"] = self.api_key
        self.model_name = model_name
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        # Default system prompt for image description
        self.system_prompt = """
You are an expert at analyzing and describing images in detail. 
Your task is to provide a clear, concise, and accurate description of the image content.

Please focus on:
1. Main subject and key elements
2. Text content if present
3. Layout and structure
4. Important details that might be relevant for document understanding

Be specific but concise in your description.
Focus on the text content and how it is structured.

Please structure your response in the following format:

[Brief description of the main subject/focus]

[Any text found in the image. Group text by the same topic together.]

[Description of layout and structure, keep it short and concise]

Keep your response clear, compact and structured but in plain text format.
Provide the description in the same language as any text found in the image. If no text is present, default to German.
"""

    def _image_to_base64(self, image: Image.Image) -> str:
        """Convert PIL Image to base64 string."""
        buffered = BytesIO()
        # Convert to RGB if necessary
        if image.mode != 'RGB':
            image = image.convert('RGB')
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')

    def describe_image(self, image: Image.Image) -> str:
        """Describe an image using the vision model.
        
        Args:
            image: PIL Image object to describe
            
        Returns:
            str: Description of the image
        """
        try:
            # Convert image to base64
            base64_image = self._image_to_base64(image)
            
            # Prepare the message for the API
            messages = [
                {
                    "role": "system", 
                    "content": self.system_prompt 
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Please describe this image in detail, following the structured format provided. Focus on text content and important visual elements."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ]
            
            # Call the API using litellm
            response = completion(
                model=self.model_name,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"Error describing image: {e}")
            return ""

def create_vision_model(
    api_key: Optional[str] = None,
    model_name: str = "gpt-4.1-mini",
    max_tokens: int = 500,
    temperature: float = 0.7
) -> VisionModel:
    """Create a vision model instance.
    
    Args:
        api_key: OpenAI API key
        model_name: Name of the OpenAI model to use
        max_tokens: Maximum number of tokens to generate
        temperature: Sampling temperature (0-1)
        
    Returns:
        VisionModel instance
    """
    return VisionModel(
        api_key=api_key,
        model_name=model_name,
        max_tokens=max_tokens,
        temperature=temperature
    )
