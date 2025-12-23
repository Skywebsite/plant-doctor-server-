"""
FastAPI application for Crop Doctor inference API.
"""

import tempfile
import os
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, status, Query
from typing import Optional, Dict
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

# Try to import inference module - handle case when ultralytics is not available
try:
    from app.inference import get_model
    INFERENCE_AVAILABLE = True
except ImportError as e:
    INFERENCE_AVAILABLE = False
    # Create a dummy function that will raise an error
    def get_model():
        raise ImportError(
            "Ultralytics YOLOv8 is not installed. "
            "This package requires Python 3.8 or higher.\n"
            "Please upgrade Python and install: pip install -r requirements.txt"
        )

from app.schemas import PredictionResponse, ErrorResponse, TranslationRequest, TranslationResponse, SupportedLanguagesResponse
from app.utils import validate_image, load_image_from_bytes, check_model_exists
from app.translator import get_translator


# Initialize FastAPI app
app = FastAPI(
    title="Crop Doctor API",
    description="YOLOv8-based plant disease detection API",
    version="1.0.0"
)

# Add CORS middleware for React/React Native frontend
# Allow specific origins for development and production
allowed_origins = [
    "http://localhost:3000",
    "https://crop-doctor-frontend-jtx7.vercel.app",
    "http://127.0.0.1:3000",
    "https://plant-doctor-server-1313.onrender.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Load model once at application startup."""
    try:
        if not check_model_exists():
            print("WARNING: Model file not found. Please train the model first.")
            print("The API will start but /predict endpoint will fail.")
        else:
            # Load model at startup (not per request)
            get_model()
            print("API started successfully!")
    except Exception as e:
        print(f"Error loading model at startup: {e}")
        print("The API will start but /predict endpoint will fail.")


@app.get("/")
async def root():
    """Root endpoint - API information."""
    return {
        "message": "Crop Doctor API",
        "version": "1.0.0",
        "endpoints": {
            "predict": "POST /predict - Upload an image to detect plant diseases",
            "health": "GET /health - Check API health status"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    model_exists = check_model_exists()
    model_loaded = False
    ultralytics_available = INFERENCE_AVAILABLE
    error_message = None
    
    try:
        get_model()
        model_loaded = True
    except ImportError as e:
        error_message = str(e)
    except Exception:
        pass
    
    return {
        "status": "healthy" if model_loaded else "degraded",
        "model_exists": model_exists,
        "model_loaded": model_loaded,
        "ultralytics_available": ultralytics_available,
        "error": error_message
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_disease(
    file: UploadFile = File(...),
    lang: Optional[str] = Query(None, description="Language code for translation (e.g., 'es', 'fr', 'hi')")
):
    """
    Predict plant disease from uploaded image.
    
    Args:
        file: Image file (multipart/form-data)
        lang: Optional language code for translation (e.g., "es", "fr", "hi")
        
    Returns:
        PredictionResponse with disease detection results (translated if lang specified)
    """
    print(f"[API] Received request with lang parameter: {lang}")
    
    # Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (JPEG, PNG, etc.)"
        )
    
    try:
        # Read file content
        file_content = await file.read()
        
        # Validate image
        is_valid, error_msg = validate_image(file_content)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_msg
            )
        
        # Load image
        image = load_image_from_bytes(file_content)
        
        # Convert to RGB if necessary (handles RGBA, L, etc.)
        if image.mode != "RGB":
            image = image.convert("RGB")
        
        # Run inference
        model = get_model()
        result = model.predict(image)
        
        # Translate if language specified
        if lang and lang != "en":
            try:
                print(f"[TRANSLATION] Translating to language: {lang}")
                translator = get_translator()
                original_disease = result.get('disease', 'N/A')
                print(f"[TRANSLATION] Original disease: {original_disease}")
                result = translator.translate_prediction_response(result, target_lang=lang)
                translated_disease = result.get('disease', 'N/A')
                print(f"[TRANSLATION] Translated disease: {translated_disease}")
            except ImportError as e:
                print(f"[TRANSLATION ERROR] Library not installed: {e}")
                print("[TRANSLATION ERROR] Run: pip install deep-translator")
            except Exception as e:
                import traceback
                print(f"[TRANSLATION ERROR] {type(e).__name__}: {e}")
                traceback.print_exc()
                # Continue with original English if translation fails
        
        # Return response
        return PredictionResponse(**result)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except ImportError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Ultralytics YOLOv8 not available: {str(e)}. Please upgrade to Python 3.8+ and install dependencies."
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model not available: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during prediction: {str(e)}"
        )


@app.get("/languages", response_model=SupportedLanguagesResponse)
async def get_supported_languages():
    """
    Get list of supported languages for translation.
    
    Returns:
        Dictionary of supported language codes and names
    """
    translator = get_translator()
    languages = translator.get_supported_languages()
    return {"languages": languages}


@app.post("/translate", response_model=TranslationResponse)
async def translate_text(request: TranslationRequest):
    """
    Translate text to target language.
    
    Args:
        request: TranslationRequest with text and target language
        
    Returns:
        Translated text
    """
    try:
        translator = get_translator()
        translated = translator.translate_text(
            request.text,
            target_lang=request.target_lang,
            source_lang=request.source_lang
        )
        return {"translated_text": translated, "target_lang": request.target_lang}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Translation error: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    import sys
    
    # Disable reload on Windows to avoid subprocess issues
    use_reload = "--reload" in sys.argv and sys.platform != "win32"
    
    # Run with uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=use_reload  # Auto-reload disabled on Windows
    )

