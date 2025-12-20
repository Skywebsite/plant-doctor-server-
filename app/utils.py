"""
Utility functions for image processing and validation.
"""

import io
from pathlib import Path
from typing import Tuple, Optional
from PIL import Image
import numpy as np


def validate_image(file_content: bytes) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded image file.
    
    Args:
        file_content: Raw bytes of the image file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Try to open the image
        image = Image.open(io.BytesIO(file_content))
        
        # Verify it's a valid image format
        image.verify()
        
        # Check if image is too large (prevent memory issues)
        max_size = 10 * 1024 * 1024  # 10MB
        if len(file_content) > max_size:
            return False, "Image file is too large (max 10MB)"
        
        return True, None
        
    except Exception as e:
        return False, f"Invalid image file: {str(e)}"


def load_image_from_bytes(file_content: bytes) -> Image.Image:
    """
    Load PIL Image from bytes.
    
    Args:
        file_content: Raw bytes of the image file
        
    Returns:
        PIL Image object
    """
    return Image.open(io.BytesIO(file_content))


def get_model_path() -> Path:
    """
    Get the path to the trained model file.
    Uses relative path from the app directory.
    
    Returns:
        Path object pointing to model/best.pt
    """
    # Get the directory where this file is located
    current_dir = Path(__file__).parent
    # Go up one level to crop_doctor_api, then into model directory
    model_path = current_dir.parent / "model" / "best.pt"
    return model_path


def check_model_exists() -> bool:
    """
    Check if the trained model file exists.
    
    Returns:
        True if model exists, False otherwise
    """
    model_path = get_model_path()
    return model_path.exists()

