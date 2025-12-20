# Plant Doctor Server (Backend)

AI-powered plant disease detection API built with FastAPI and YOLOv8.

## Features

- 🚀 FastAPI-based REST API
- 🤖 YOLOv8 model for plant disease detection
- 🌍 Multi-language support (30+ languages)
- 📸 Image annotation with bounding boxes
- 🔄 Real-time disease detection
- 📊 Confidence scoring

## Installation

### Prerequisites

- Python 3.8 or higher
- CUDA-enabled GPU (recommended) or CPU

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your trained model in the `model/` directory:
   - `model/best.pt` - Your trained YOLOv8 model

3. Start the API server:
```bash
python start_api.py
```

The API will be available at `http://localhost:8000`

## API Endpoints

### POST /predict
Upload an image to detect plant diseases.

**Parameters:**
- `file`: Image file (multipart/form-data)
- `lang`: Optional language code for translation (e.g., "es", "fr", "hi")

**Response:**
```json
{
  "disease": "Leaf Spot",
  "confidence": 0.95,
  "all_predictions": [...],
  "annotated_image": "data:image/png;base64,..."
}
```

### GET /languages
Get list of supported languages for translation.

### POST /translate
Translate text to target language.

### GET /health
Health check endpoint.

## Training

Train your own model using the training script:

```bash
python train/train.py --data "path/to/data.yaml" --epochs 100 --batch 16 --model yolov8s.pt
```

See `train/train.py` for more options.

## Project Structure

```
crop_doctor_api/
├── app/
│   ├── main.py          # FastAPI application
│   ├── inference.py     # Model inference logic
│   ├── translator.py    # Translation service
│   ├── schemas.py       # Pydantic models
│   └── utils.py         # Utility functions
├── train/
│   └── train.py         # Training script
├── model/
│   └── best.pt          # Trained model (not in repo)
└── requirements.txt     # Python dependencies
```

## License

Open source - feel free to use and modify.
