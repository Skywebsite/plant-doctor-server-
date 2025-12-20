# ⚠️ Python Version Warning

You are currently using **Python 3.7.0**, but this project requires **Python 3.8 or higher**.

## Why?

Ultralytics YOLOv8 requires:
- Python >= 3.8
- NumPy >= 1.22.2 (which also requires Python >= 3.8)

## How to Upgrade Python

### Windows
1. Download Python 3.10 or 3.11 from [python.org](https://www.python.org/downloads/)
2. Run the installer
3. **Important**: Check "Add Python to PATH" during installation
4. Restart your terminal/PowerShell
5. Verify: `python --version` should show 3.8+

### Using pyenv (Recommended for Multiple Python Versions)
```bash
# Install pyenv-win (Windows)
# Follow: https://github.com/pyenv-win/pyenv-win

pyenv install 3.10.11
pyenv local 3.10.11
```

### Verify Installation
```bash
python --version
# Should show: Python 3.8.x or higher
```

## After Upgrading

1. Create a new virtual environment:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Alternative: Use Python 3.7 Compatible Versions (Not Recommended)

If you absolutely cannot upgrade Python, you would need to use older versions of the libraries, but this is **not recommended** because:
- Ultralytics YOLOv8 won't work with Python 3.7
- You'll miss important bug fixes and features
- Security vulnerabilities in older versions

**Strongly recommend upgrading to Python 3.8+ for best results.**

