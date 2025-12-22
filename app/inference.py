"""
YOLO model inference module.
Handles model loading and prediction.
"""

import os
import io
import base64
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Try to import ultralytics - handle case when it's not installed (Python 3.7)
try:
    import torch
    from ultralytics import YOLO
    # Fix for PyTorch 2.6+ weights_only default change
    # Add Ultralytics classes to safe globals for model loading
    try:
        from ultralytics.nn.tasks import DetectionModel
        torch.serialization.add_safe_globals([DetectionModel])
    except (ImportError, AttributeError):
        # If add_safe_globals doesn't exist or import fails, 
        # we'll handle it in the model loading
        pass
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False
    YOLO = None  # type: ignore

from app.utils import get_model_path, load_image_from_bytes
from app.schemas import PredictionItem


class ModelInference:
    """
    YOLO model inference handler.
    Loads model once at initialization for efficient inference.
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize the inference handler.
        
        Args:
            model_path: Path to the trained model. If None, uses default path.
        """
        # Check if ultralytics is available
        if not ULTRALYTICS_AVAILABLE:
            raise ImportError(
                "Ultralytics YOLOv8 is not installed. "
                "This package requires Python 3.8 or higher.\n"
                "Please upgrade Python and install: pip install -r requirements.txt\n"
                "See PYTHON_VERSION_WARNING.md for upgrade instructions."
            )
        
        if model_path is None:
            model_path = get_model_path()
        
        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            raise FileNotFoundError(
                f"Model file not found at: {self.model_path.absolute()}\n"
                "Please train the model first using train/train.py"
            )
        
        print(f"Loading YOLO model from: {self.model_path.absolute()}")
        
        # Fix for PyTorch 2.6+ weights_only issue
        # Patch torch.load to use weights_only=False before loading model
        import torch
        original_load = torch.load
        
        def patched_load(*args, **kwargs):
            # Always set weights_only=False for model loading
            if 'weights_only' not in kwargs:
                kwargs['weights_only'] = False
            return original_load(*args, **kwargs)
        
        # Apply patch
        torch.load = patched_load
        
        try:
            # Try to add safe globals if method exists
            try:
                from ultralytics.nn.tasks import DetectionModel
                if hasattr(torch.serialization, 'add_safe_globals'):
                    torch.serialization.add_safe_globals([DetectionModel])
            except (ImportError, AttributeError):
                pass
            
            # Load model with patched torch.load
            self.model = YOLO(str(self.model_path))
        finally:
            # Restore original torch.load after model loading
            torch.load = original_load
        
        print("Model loaded successfully!")
    
    def predict(self, image: Image.Image) -> Dict:
        """
        Run inference on an image.
        
        Args:
            image: PIL Image object
            
        Returns:
            Dictionary with prediction results:
            {
                "disease": str,
                "confidence": float,
                "all_predictions": List[PredictionItem],
                "annotated_image": str (base64-encoded PNG image with bounding boxes)
            }
        """
        # Run YOLO inference
        # Results is a list of Results objects
        results = self.model(image, verbose=False)
        
        # Get the first result (single image inference)
        result = results[0]
        
        # Extract predictions
        boxes = result.boxes
        
        # Get all detected classes with confidence scores
        all_predictions = []
        
        # Create a copy of the image for annotation
        annotated_image = image.copy()
        draw = ImageDraw.Draw(annotated_image)
        
        # Try to load a font (fallback to default if not available)
        font = None
        try:
            # Try common font paths
            font_paths = [
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
                "C:/Windows/Fonts/arial.ttf",  # Windows
            ]
            for font_path in font_paths:
                try:
                    if os.path.exists(font_path):
                        font = ImageFont.truetype(font_path, 16)
                        break
                except:
                    continue
            # Fallback to default font if nothing worked
            if font is None:
                font = ImageFont.load_default()
        except:
            font = None
        
        if boxes is not None and len(boxes) > 0:
            # Get class names and confidences
            class_ids = boxes.cls.cpu().numpy()
            confidences = boxes.conf.cpu().numpy()
            box_coords = boxes.xyxy.cpu().numpy()  # Get bounding box coordinates
            
            # Get class names from the model
            class_names = result.names
            
            # Colors for different classes (cycle through colors)
            colors = [
                (255, 0, 0),    # Red
                (0, 255, 0),    # Green
                (0, 0, 255),    # Blue
                (255, 255, 0),  # Yellow
                (255, 0, 255),  # Magenta
                (0, 255, 255),  # Cyan
                (255, 128, 0),  # Orange
                (128, 0, 255),  # Purple
            ]
            
            # Draw bounding boxes and labels
            for i, (box, class_id, confidence) in enumerate(zip(box_coords, class_ids, confidences)):
                class_name = class_names[int(class_id)]
                color = colors[int(class_id) % len(colors)]
                
                # Draw bounding box
                x1, y1, x2, y2 = box
                draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=3)
                
                # Prepare label text
                label = f"{class_name}: {confidence:.2f}"
                
                # Calculate text size and position
                try:
                    if font:
                        # Try textbbox first (PIL 8.0+)
                        try:
                            bbox = draw.textbbox((0, 0), label, font=font)
                            text_width = bbox[2] - bbox[0]
                            text_height = bbox[3] - bbox[1]
                        except AttributeError:
                            # Fallback to textsize (older PIL)
                            text_width, text_height = draw.textsize(label, font=font)
                    else:
                        # Estimate size without font
                        text_width = len(label) * 6
                        text_height = 12
                except:
                    # Fallback estimation
                    text_width = len(label) * 6
                    text_height = 12
                
                # Draw label background
                label_y = max(0, y1 - text_height - 5)
                draw.rectangle(
                    [(x1, label_y), (x1 + text_width + 10, label_y + text_height + 5)],
                    fill=color
                )
                
                # Draw label text
                if font:
                    draw.text((x1 + 5, label_y + 2), label, fill=(255, 255, 255), font=font)
                else:
                    draw.text((x1 + 5, label_y + 2), label, fill=(255, 255, 255))
                
                # Create prediction items
                all_predictions.append(
                    PredictionItem(
                        class_name=class_name,
                        confidence=float(confidence)
                    )
                )
            
            # Sort by confidence (highest first)
            all_predictions.sort(key=lambda x: x.confidence, reverse=True)
            
            # Get primary prediction (highest confidence)
            primary = all_predictions[0]
            disease = primary.class_name
            confidence = primary.confidence
            
        else:
            # No detections - return default response
            disease = "No Disease Detected"
            confidence = 0.0
            all_predictions = [
                PredictionItem(class_name="No Disease Detected", confidence=0.0)
            ]
        
        # Convert annotated image to base64 string
        img_buffer = io.BytesIO()
        annotated_image.save(img_buffer, format='PNG')
        img_str = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        annotated_image_base64 = f"data:image/png;base64,{img_str}"
        
        return {
            "disease": disease,
            "confidence": confidence,
            "all_predictions": all_predictions,
            "annotated_image": annotated_image_base64
        }


# Global model instance (loaded once at startup)
_model_instance: ModelInference = None


def get_model() -> ModelInference:
    """
    Get or create the global model instance.
    This ensures the model is loaded only once.
    
    Returns:
        ModelInference instance
    """
    global _model_instance
    if _model_instance is None:
        _model_instance = ModelInference()
    return _model_instance

