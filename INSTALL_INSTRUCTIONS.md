# Installation Instructions

## Quick Start

You have Python 3.12.7 installed! Use the `py` command instead of `python` or `pip`.

### Install Dependencies

```powershell
cd crop_doctor_api
py -m pip install -r requirements.txt
```

**Note**: This will take 5-10 minutes as it downloads large packages like PyTorch (~110MB) and OpenCV (~39MB). Please be patient and let it complete.

### Start the API Server

```powershell
py start_api.py
```

Or:

```powershell
py -m uvicorn app.main:app --reload
```

### Start the Frontend

In a new terminal:

```powershell
cd crop_doctor_frontend
npm install
npm start
```

## Troubleshooting

### If pip command doesn't work

Always use:
```powershell
py -m pip install <package>
```

Instead of:
```powershell
pip install <package>  # This might not work
```

### If installation is slow

The packages are large. This is normal. Let it complete.

### If you see PATH warnings

These are just warnings. The packages will still work. You can ignore them.

