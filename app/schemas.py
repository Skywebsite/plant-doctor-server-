"""
Pydantic schemas for API request/response models.
Compatible with both Pydantic 1.x (Python 3.7) and 2.x (Python 3.8+).
"""

from typing import List, Optional, Dict
from pydantic import BaseModel, Field


class PredictionItem(BaseModel):
    """Individual prediction result."""
    class_name: str = Field(..., description="Detected disease class name")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score (0-1)")


class PredictionResponse(BaseModel):
    """API response model for disease prediction."""
    disease: str = Field(..., description="Primary detected disease (highest confidence)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score of primary disease")
    all_predictions: List[PredictionItem] = Field(
        ..., 
        description="All detected diseases with confidence scores"
    )
    annotated_image: str = Field(
        ..., 
        description="Base64-encoded annotated image with bounding boxes (data:image/png;base64,...)"
    )


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Additional error details")


class TranslationRequest(BaseModel):
    """Translation request model."""
    text: str = Field(..., description="Text to translate")
    target_lang: str = Field(..., description="Target language code (e.g., 'es', 'fr', 'hi')")
    source_lang: str = Field(default="en", description="Source language code (default: 'en')")


class TranslationResponse(BaseModel):
    """Translation response model."""
    translated_text: str = Field(..., description="Translated text")
    target_lang: str = Field(..., description="Target language code")


class SupportedLanguagesResponse(BaseModel):
    """Supported languages response model."""
    languages: Dict[str, str] = Field(..., description="Dictionary of language codes and names")

