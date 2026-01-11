# AI Image Generator - Deployment Guide

## 🌐 Live Demo

**Frontend**: https://powerx1.github.io/ai-image-generator/AI-Image-Web/

## 📋 Deployment Status

| Component | Status | URL |
|-----------|--------|-----|
| Frontend (HTML/CSS/JS) | ✅ Hosted | GitHub Pages |
| Backend API | 🔧 Local | Run on your machine |
| Stable Diffusion WebUI | 🔧 Local | Requires GPU |

## Why This Setup?

Your AI Image Generator requires:
- **Large AI models** (several GB) - too big for free hosting
- **GPU processing** - expensive cloud resources ($50-500/month)
- **Stable Diffusion WebUI** - resource-intensive

**Solution**: Host the frontend online for portfolio, run backend locally for demonstrations.

---

## 🚀 Frontend Deployment (GitHub Pages)

### Already Deployed! ✅

Your frontend is live at: https://powerx1.github.io/ai-image-generator/AI-Image-Web/

### What's Hosted:
- ✅ Main page (Text-to-Image UI)
- ✅ Img2Img page
- ✅ Img2Text page
- ✅ Login/Signup pages
- ✅ All CSS and JavaScript

---

## 🖥️ Backend Deployment Options

### Option 1: Local Demo (Recommended for Students)

**Best for**: Presentations, demonstrations, portfolio reviews

1. Run Stable Diffusion WebUI locally:
```bash
cd stable-diffusion-webui
webui-user.bat
```

2. Run the API:
```bash
cd AI-Image-Web
python -m uvicorn api:app --host 0.0.0.0 --port 8000
```

3. Update frontend to use your local API (during demos)

**Pros**: Free, full functionality, fast
**Cons**: Only works when your computer is running

---

### Option 2: Cloud Deployment (Advanced)

#### A. Backend API Only (Free Tier)

**Render.com** - Deploy FastAPI backend
- Free tier: 750 hours/month
- Includes database
- Auto-deploy from GitHub

**Steps**:
1. Go to https://render.com
2. Sign up with GitHub
3. Create "New Web Service"
4. Connect your repository
5. Use these settings:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn AI-Image-Web.api:app --host 0.0.0.0 --port $PORT`

**Limitation**: No Stable Diffusion (requires GPU)

#### B. Full Stack with GPU (Paid)

**RunPod.io** - GPU instances
- Cost: $0.20-$1.50/hour
- Supports Stable Diffusion

**Vast.ai** - Cheap GPU rental
- Cost: $0.10-$0.50/hour

---

## 🎯 Recommended Setup for Your Project

### For Portfolio/GitHub:
✅ Frontend on GitHub Pages (done!)
✅ Backend code visible on GitHub
✅ Clear README with setup instructions
✅ Demo video or screenshots

### For Live Demonstrations:
1. Run everything locally
2. Use ngrok to create temporary public URL:
```bash
ngrok http 8000
```

### For Presentation:
- Show the live frontend: https://powerx1.github.io/ai-image-generator/AI-Image-Web/
- Demo backend locally
- Explain the architecture

---

## 📝 Update Frontend API URL

If you deploy the backend, update the API URL in:
- `AI-Image-Web/control.js`
- `AI-Image-Web/img2text.js`
- `AI-Image-Web/auth.js`

Change from:
```javascript
fetch('http://127.0.0.1:8000/generate', ...)
```

To:
```javascript
fetch('https://your-backend-url.com/generate', ...)
```

---

## 💡 Pro Tips

1. **For Interviews**: Record a demo video showing full functionality
2. **For GitHub**: Add badges showing it's deployed
3. **For Portfolio**: Explain the architecture in README
4. **Cost-Free**: Use local setup for all demos

---

## 🆘 Need Help?

- Frontend not loading? Check GitHub Pages settings
- CORS errors? Update API CORS settings
- Want to deploy backend? Follow Render.com guide above
