"""
YOLOv8 Training Script for Crop Doctor
Trains a YOLOv8 model on plant disease detection dataset.
"""

import argparse
import os
from pathlib import Path
from ultralytics import YOLO
import torch


def train_model(
    data_yaml: str,
    epochs: int = 50,
    batch: int = 16,
    imgsz: int = 640,
    model_name: str = "yolov8n.pt",
    output_dir: str = "../model"
):
    """
    Train YOLOv8 model on plant disease dataset.
    
    Args:
        data_yaml: Path to data.yaml file (from Roboflow dataset)
        epochs: Number of training epochs
        batch: Batch size
        imgsz: Image size for training
        model_name: Pretrained model name (yolov8n.pt, yolov8s.pt, etc.)
        output_dir: Directory to save the best model
    """
    # Convert to Path objects for easier handling
    data_yaml_path = Path(data_yaml)
    output_path = Path(output_dir)
    
    # Validate data.yaml exists
    if not data_yaml_path.exists():
        raise FileNotFoundError(f"data.yaml not found at: {data_yaml_path}")
    
    # Create output directory if it doesn't exist
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Check GPU availability
    device = 0 if torch.cuda.is_available() else 'cpu'
    if torch.cuda.is_available():
        print(f"✓ CUDA available! Using GPU: {torch.cuda.get_device_name(0)}")
        print(f"  GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
    else:
        print("⚠ CUDA not available. Training on CPU (will be slow!)")
    
    print(f"\nLoading pretrained model: {model_name}")
    # Load pretrained YOLOv8 model
    model = YOLO(model_name)
    
    print(f"\nStarting training with:")
    print(f"  - Data: {data_yaml_path}")
    print(f"  - Epochs: {epochs}")
    print(f"  - Batch size: {batch}")
    print(f"  - Image size: {imgsz}")
    print(f"  - Device: {'GPU (CUDA)' if device == 0 else 'CPU'}")
    print(f"  - Output directory: {output_path.absolute()}")
    
    # Train the model with explicit device specification
    results = model.train(
        data=str(data_yaml_path),
        epochs=epochs,
        batch=batch,
        imgsz=imgsz,
        device=device,  # Explicitly set device (0 for GPU, 'cpu' for CPU)
        project=str(output_path.parent),
        name="runs",
        exist_ok=True,
        save=True,
        verbose=True
    )
    
    # Copy best.pt to model directory
    # The best model is saved in runs/train/weights/best.pt
    runs_dir = output_path.parent / "runs" / "train"
    best_model_path = None
    
    # Find the latest training run
    if runs_dir.exists():
        train_dirs = sorted([d for d in runs_dir.iterdir() if d.is_dir()], 
                           key=lambda x: x.stat().st_mtime, reverse=True)
        if train_dirs:
            weights_dir = train_dirs[0] / "weights"
            best_model = weights_dir / "best.pt"
            if best_model.exists():
                best_model_path = best_model
    
    if best_model_path and best_model_path.exists():
        import shutil
        target_path = output_path / "best.pt"
        print(f"\nCopying best model to: {target_path}")
        shutil.copy2(best_model_path, target_path)
        print(f"Training complete! Best model saved to: {target_path.absolute()}")
    else:
        print("\nWarning: Could not find best.pt in training runs.")
        print("Please check the runs/train directory manually.")
    
    return results


def main():
    """Main entry point for training script."""
    parser = argparse.ArgumentParser(
        description="Train YOLOv8 model for crop disease detection"
    )
    parser.add_argument(
        "--data",
        type=str,
        required=True,
        help="Path to data.yaml file (e.g., ../Detecting diseases.v1i.yolov8-obb/data.yaml)"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=50,
        help="Number of training epochs (default: 50)"
    )
    parser.add_argument(
        "--batch",
        type=int,
        default=16,
        help="Batch size (default: 16)"
    )
    parser.add_argument(
        "--imgsz",
        type=int,
        default=640,
        help="Image size for training (default: 640)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="yolov8n.pt",
        help="Pretrained model name (default: yolov8n.pt)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="../model",
        help="Output directory for best.pt (default: ../model)"
    )
    
    args = parser.parse_args()
    
    try:
        train_model(
            data_yaml=args.data,
            epochs=args.epochs,
            batch=args.batch,
            imgsz=args.imgsz,
            model_name=args.model,
            output_dir=args.output
        )
    except Exception as e:
        print(f"Error during training: {e}")
        raise


if __name__ == "__main__":
    main()

