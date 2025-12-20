"""
Vercel serverless entry point for Crop Doctor API.
This file adapts the FastAPI app for Vercel's serverless functions.
"""

import sys
from pathlib import Path

# Add app directory to path
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

# Import FastAPI app
from app.main import app

# Vercel expects the handler to be named 'app' or 'handler'
# FastAPI apps work directly with Vercel
__all__ = ['app']
