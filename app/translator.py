"""
Translation service for multi-language support.
Uses deep-translator for reliable translations.
"""

from typing import Dict, List, Optional
from deep_translator import GoogleTranslator


# Supported languages mapping
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish", 
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "zh": "Chinese (Simplified)",
    "ja": "Japanese",
    "ko": "Korean",
    "ar": "Arabic",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "ml": "Malayalam",
    "kn": "Kannada",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "ur": "Urdu",
    "pa": "Punjabi",
    "ne": "Nepali",
    "si": "Sinhala",
    "my": "Myanmar",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "ms": "Malay",
    "tl": "Filipino",
}


class TranslationService:
    """Service for translating disease names and text."""
    
    def __init__(self):
        """Initialize translation service."""
        self.supported_langs = SUPPORTED_LANGUAGES
    
    def translate_text(self, text: str, target_lang: str = "en", source_lang: str = "en") -> str:
        """
        Translate a single text string.
        
        Args:
            text: Text to translate
            target_lang: Target language code (default: "en")
            source_lang: Source language code (default: "en")
            
        Returns:
            Translated text
        """
        if target_lang == "en" or target_lang == source_lang:
            return text
        
        try:
            translator = GoogleTranslator(source=source_lang, target=target_lang)
            translated = translator.translate(text)
            return translated
        except Exception as e:
            print(f"Translation error for '{text}': {e}")
            return text  # Return original text on error
    
    def translate_disease_names(self, predictions: List, target_lang: str = "en") -> List[Dict]:
        """
        Translate disease names in prediction results.
        
        Args:
            predictions: List of prediction dictionaries or Pydantic models with 'class_name' key
            target_lang: Target language code (default: "en")
            
        Returns:
            List of prediction dictionaries with translated class names
        """
        if target_lang == "en":
            # Convert to dicts if needed
            result = []
            for pred in predictions:
                if hasattr(pred, 'dict'):
                    result.append(pred.dict())
                elif hasattr(pred, 'model_dump'):
                    result.append(pred.model_dump())
                elif isinstance(pred, dict):
                    result.append(pred)
                else:
                    result.append({"class_name": str(pred), "confidence": 0.0})
            return result
        
        translated_predictions = []
        for pred in predictions:
            # Convert Pydantic model to dict if needed
            if hasattr(pred, 'dict'):
                pred_dict = pred.dict()
            elif hasattr(pred, 'model_dump'):
                pred_dict = pred.model_dump()
            elif isinstance(pred, dict):
                pred_dict = pred.copy()
            else:
                pred_dict = {"class_name": str(pred), "confidence": 0.0}
            
            original_name = pred_dict.get("class_name", "")
            translated_name = self.translate_text(original_name, target_lang=target_lang)
            pred_dict["class_name"] = translated_name
            translated_predictions.append(pred_dict)
        
        return translated_predictions
    
    def translate_prediction_response(self, response: Dict, target_lang: str = "en") -> Dict:
        """
        Translate entire prediction response.
        
        Args:
            response: Prediction response dictionary
            target_lang: Target language code (default: "en")
            
        Returns:
            Translated response dictionary
        """
        if target_lang == "en":
            return response
        
        translated_response = response.copy()
        
        # Translate primary disease name
        if "disease" in translated_response:
            original_disease = translated_response["disease"]
            translated_disease = self.translate_text(original_disease, target_lang=target_lang)
            translated_response["disease"] = translated_disease
            print(f"[TRANSLATOR] '{original_disease}' -> '{translated_disease}' ({target_lang})")
        
        # Translate all predictions
        if "all_predictions" in translated_response:
            predictions = translated_response["all_predictions"]
            translated_predictions = self.translate_disease_names(
                predictions,
                target_lang=target_lang
            )
            translated_response["all_predictions"] = translated_predictions
        
        return translated_response
    
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get dictionary of supported language codes and names.
        
        Returns:
            Dictionary mapping language codes to language names
        """
        return self.supported_langs.copy()


# Global translation service instance
_translation_service = None


def get_translator() -> TranslationService:
    """
    Get or create the global translation service instance.
    
    Returns:
        TranslationService instance
    """
    global _translation_service
    if _translation_service is None:
        _translation_service = TranslationService()
    return _translation_service
