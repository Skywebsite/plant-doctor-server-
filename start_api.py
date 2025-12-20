"""
Quick start script for the Crop Doctor API.
Run this from the crop_doctor_api directory.
"""

import uvicorn
import sys

if __name__ == "__main__":
    # Disable reload on Windows to avoid subprocess issues
    # Set reload=True for development on Linux/macOS if needed
    use_reload = "--reload" in sys.argv and sys.platform != "win32"
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=use_reload
    )

