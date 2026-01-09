# Setup Instructions

## Quick Start

### 1. Run the API Server

```bash
cd "C:\Users\gaming corner\Desktop\final project\AI-Image-Web"

# Option A: Using FastAPI (Recommended)
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# Option B: Using Flask
python api_flask.py
```

### 2. Run the Frontend Server

```bash
cd "C:\Users\gaming corner\Desktop\final project\AI-Image-Web"
python serve.py 5500
```

### 3. Start Stable Diffusion WebUI

```bash
cd "C:\Users\gaming corner\Desktop\final project\stable-diffusion-webui"
webui-user.bat
```

### 4. Open in Browser

Navigate to: http://localhost:5500/index.html

## Environment Variables

Copy `.env.example` to `.env` and configure:

- `STABLE_URL`: URL of your Stable Diffusion WebUI (default: http://127.0.0.1:7861)

## Troubleshooting

- Make sure all three services are running (WebUI, API, Frontend)
- Check that ports 5500, 7861, and 8000 are available
- Ensure you have a Stable Diffusion model downloaded
