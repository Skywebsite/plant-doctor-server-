# Vercel Deployment Guide for Crop Doctor API

## ⚠️ Important Considerations

**Vercel Limitations for ML Models:**
- **Function timeout**: 60 seconds (free tier: 10 seconds, Pro: up to 60 seconds)
- **Memory limit**: 1GB (free tier), 3GB (Pro)
- **Cold starts**: Model loading takes ~2-5 seconds on first request
- **File size**: Model file (6MB) is within limits, but deployment may be slow

**Recommendation**: For production ML inference, consider Render or Railway instead. Vercel works but may have slower cold starts.

---

## Prerequisites

1. **Vercel Account**: Sign up at https://vercel.com
2. **Vercel CLI**: Install globally
   ```bash
   npm install -g vercel
   ```
3. **GitHub Repository**: Your code should be in GitHub (already done ✅)

---

## Deployment Steps

### Method 1: Using Vercel Dashboard (Recommended)

1. **Go to Vercel Dashboard**
   - Visit: https://vercel.com/dashboard
   - Click "Add New Project"

2. **Import Git Repository**
   - Select "Import Git Repository"
   - Choose your repository: `Skywebsite/plant-doctor-server-`
   - Click "Import"

3. **Configure Project**
   - **Root Directory**: `crop_doctor_api` (if repo is root, leave blank)
   - **Framework Preset**: Other
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
   - **Install Command**: `pip install -r requirements.txt`

4. **Environment Variables** (if needed later)
   - Add any environment variables if you add them in the future

5. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete (~2-5 minutes)

6. **Get Your API URL**
   - After deployment, you'll get a URL like: `https://your-project.vercel.app`
   - Your API will be available at: `https://your-project.vercel.app/api/...`

---

### Method 2: Using Vercel CLI

1. **Navigate to project directory**
   ```bash
   cd c:\Users\lenovo\Desktop\cropdoctor\crop_doctor_api
   ```

2. **Login to Vercel**
   ```bash
   vercel login
   ```

3. **Deploy**
   ```bash
   vercel
   ```
   - Follow prompts:
     - Set up and deploy? **Yes**
     - Which scope? (select your account)
     - Link to existing project? **No**
     - Project name? (enter a name or press Enter)
     - In which directory is your code located? `./`
     - Want to override settings? **No**

4. **Production Deployment**
   ```bash
   vercel --prod
   ```

---

## Project Structure for Vercel

```
crop_doctor_api/
├── api/
│   └── index.py          # Vercel serverless entry point
├── app/
│   ├── __init__.py
│   ├── main.py           # FastAPI app
│   ├── inference.py
│   ├── schemas.py
│   ├── translator.py
│   └── utils.py
├── model/
│   └── best.pt           # Trained model (6MB)
├── requirements.txt
├── vercel.json           # Vercel configuration
└── .vercelignore
```

---

## API Endpoints

After deployment, your API will be available at:
- Base URL: `https://your-project.vercel.app`

Endpoints:
- `GET /` - API information
- `GET /health` - Health check
- `POST /predict?lang=es` - Disease prediction (with optional translation)
- `GET /languages` - Supported languages
- `POST /translate` - Translate text

**Note**: Vercel routes everything through `/api/index`, so endpoints work as expected.

---

## Updating Frontend API URL

After deployment, update your frontend to use the Vercel URL:

**File**: `crop_doctor_frontend/src/App.js`

```javascript
// Change from:
const response = await fetch('http://localhost:8000/predict', {

// To:
const response = await fetch('https://your-project.vercel.app/predict', {
```

Also update the translation endpoint:
```javascript
const diseaseTranslation = await fetch('https://your-project.vercel.app/translate', {
```

---

## Troubleshooting

### Issue: Function timeout
**Solution**: Upgrade to Vercel Pro for 60-second timeout, or optimize model loading

### Issue: Cold start too slow
**Solution**: This is normal for serverless. First request takes ~5-10 seconds to load model.

### Issue: Model file too large
**Solution**: The 6MB model is within limits. If issues, consider using model compression.

### Issue: Memory limit exceeded
**Solution**: 
- Vercel free tier: 1GB (might be tight for YOLO)
- Upgrade to Pro for 3GB
- Or use Render/Railway instead

### Issue: Import errors
**Solution**: Ensure all dependencies are in `requirements.txt`

---

## Performance Optimization Tips

1. **Keep function warm**: Use a cron job to ping `/health` every 5 minutes
2. **Use Pro plan**: For better performance and limits
3. **Optimize model**: Consider using quantized or smaller model
4. **Cache translations**: Store common translations to reduce API calls

---

## Cost Comparison

- **Vercel Free Tier**: 
  - 100GB bandwidth/month
  - 100 hours function execution
  - 10-second function timeout
  - 1GB memory
  - ✅ Free, but limited for ML

- **Vercel Pro**: $20/month
  - Unlimited bandwidth
  - Unlimited function execution
  - 60-second function timeout
  - 3GB memory
  - Better for production ML

---

## Alternative: Use Vercel for Frontend Only

If Vercel backend has issues, consider:
- **Frontend**: Deploy React app on Vercel (excellent for this)
- **Backend**: Deploy FastAPI on Render or Railway (better for ML)

This gives you the best of both worlds!

---

## Next Steps

1. Deploy backend to Vercel using steps above
2. Update frontend API URLs to Vercel backend URL
3. Deploy frontend (can also use Vercel - it's great for React!)
4. Test all endpoints
5. Monitor performance and consider Pro plan if needed

---

**Good luck with your deployment! 🚀**
