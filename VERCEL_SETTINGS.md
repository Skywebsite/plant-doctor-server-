# Vercel Deployment Settings

## Build & Install Commands Configuration

When setting up your project in Vercel Dashboard, use these settings:

### Build Command
```
(Leave empty/None)
```
**Why**: Python projects don't need a build step. Vercel automatically handles Python deployments.

### Output Directory
```
(Leave empty/N/A)
```
**Why**: Not needed for API/backend projects. Only needed for static site generators.

### Install Command
```
pip install -r requirements.txt
```
**OR** (if using Pipfile):
```
pipenv install
```

**Why**: This installs all Python dependencies before deployment.

---

## Recommended Vercel Dashboard Settings

1. **Root Directory**: `crop_doctor_api` (if your repo root is cropdoctor, otherwise leave blank)

2. **Framework Preset**: `Other`

3. **Build Command**: (Leave empty)

4. **Output Directory**: (Leave empty)

5. **Install Command**: `pip install -r requirements.txt`

6. **Development Command**: (Leave empty)

7. **Node.js Version**: (Not needed for Python)

---

## Alternative: Zero Configuration

Vercel supports **zero-configuration** for FastAPI. If you have:
- `requirements.txt` or `Pipfile` in root
- `api/` directory with Python files
- FastAPI app structure

You can **leave all commands empty** and Vercel will auto-detect and configure everything!

---

## After Deployment

Your API will be available at:
- `https://your-project.vercel.app/api/...`
- Example: `https://your-project.vercel.app/predict`
- Example: `https://your-project.vercel.app/health`
