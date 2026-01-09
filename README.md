# 🎨 AI Image Generator Web Application

A modern web application for AI-powered image generation using Stable Diffusion. Features text-to-image generation, image-to-image transformation, and image-to-text captioning capabilities.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

- **Text-to-Image (txt2img)**: Generate stunning images from text prompts
- **Image-to-Image (img2img)**: Transform existing images with AI guidance
- **Image-to-Text (img2text)**: Generate captions and descriptions for images using BLIP model
- **Modern UI**: Beautiful, responsive interface with dark theme
- **Real-time Preview**: Instant feedback on generated images
- **Customizable Parameters**: Control steps, CFG scale, dimensions, samplers, and more

## 🖼️ Screenshots

The application includes three main pages:
- **Gallery** - Main text-to-image generation interface
- **Img2Img** - Image transformation tool
- **Img2Text** - AI image captioning

## 🛠️ Tech Stack

### Frontend
- HTML5, CSS3, JavaScript
- Font Awesome icons
- Google Fonts (Inter)

### Backend
- **FastAPI** (primary) / Flask (alternative)
- Python 3.8+
- Pillow for image processing
- Transformers (BLIP model for image captioning)

### AI Backend
- Stable Diffusion WebUI (AUTOMATIC1111)
- PyTorch with CUDA support (optional)

## 📋 Prerequisites

- Python 3.8 or higher
- Stable Diffusion WebUI installed and running
- 8GB+ RAM (16GB recommended)
- GPU with 4GB+ VRAM (optional, but recommended)

## 🚀 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/ai-image-generator.git
cd ai-image-generator
```

### 2. Create Virtual Environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux/macOS
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup Stable Diffusion WebUI

Clone the Stable Diffusion WebUI repository separately:

```bash
git clone https://github.com/AUTOMATIC1111/stable-diffusion-webui.git
```

Then follow these steps:
1. Download a Stable Diffusion model (e.g., SD 1.5, SDXL) from [Hugging Face](https://huggingface.co/models?other=stable-diffusion) or [Civitai](https://civitai.com/)
2. Place the model in `stable-diffusion-webui/models/Stable-diffusion/`
3. Enable API access by adding `--api` flag to launch arguments in `webui-user.bat` or `webui-user.sh`

## 🏃 Running the Application

### Step 1: Start Stable Diffusion WebUI

```bash
# Windows
cd stable-diffusion-webui
webui-user.bat

# Linux/macOS
cd stable-diffusion-webui
./webui.sh
```

The WebUI should start on `http://127.0.0.1:7861` by default.

### Step 2: Start the API Server

```bash
cd AI-Image-Web

# Using FastAPI (recommended)
python -m uvicorn api:app --host 0.0.0.0 --port 8000 --reload

# OR using Flask
python api_flask.py
```

### Step 3: Serve the Frontend

```bash
# Using the built-in server
python serve.py 5500
```

### Step 4: Open the Application

Visit `http://localhost:5500/index.html` in your browser.

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `STABLE_URL` | `http://127.0.0.1:7861` | Stable Diffusion WebUI API URL |

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/generate` | POST | Generate image (txt2img or img2img) |
| `/img2text` | POST | Generate image caption |

### Request Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `prompt` | string | required | Text prompt for generation |
| `negative_prompt` | string | "" | Negative prompt |
| `steps` | int | 30 | Number of inference steps |
| `cfg_scale` | float | 7.0 | Classifier-free guidance scale |
| `width` | int | 512 | Output image width |
| `height` | int | 512 | Output image height |
| `sampler_name` | string | "DPM++ 2M Karras" | Sampling method |
| `seed` | int | -1 | Random seed (-1 for random) |
| `mode` | string | "txt2img" | Generation mode |
| `denoising_strength` | float | 0.75 | Denoising strength (img2img) |
| `init_image` | file | null | Initial image (img2img) |

## 📁 Project Structure

```
ai-image-generator/
├── AI-Image-Web/              # Main web application
│   ├── api.py                 # FastAPI backend
│   ├── api_flask.py           # Flask backend (alternative)
│   ├── serve.py               # Static file server
│   ├── index.html             # Main page (txt2img)
│   ├── img2img.html           # Image-to-image page
│   ├── img2text.html          # Image-to-text page
│   ├── control.js             # Frontend JavaScript
│   ├── img2text.js            # Img2text functionality
│   ├── *.css                  # Stylesheets
│   ├── requirements.txt       # Python dependencies
│   └── output/                # Generated images
├── stable-diffusion-webui/    # Stable Diffusion WebUI (clone separately)
├── .github/                   # GitHub configuration
├── .env.example               # Environment variables template
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Main dependencies
├── LICENSE                    # MIT License
├── CONTRIBUTING.md            # Contribution guidelines
└── README.md                  # This file
```

## 🔧 Troubleshooting

### Common Issues

**1. CORS Error**
- Make sure the API server is running on port 8000
- Check that CORS is properly configured in `api.py`

**2. Connection Refused to Stable Diffusion**
- Ensure WebUI is running with `--api` flag
- Check `STABLE_URL` environment variable
- Verify the port (default: 7861)

**3. Out of Memory**
- Reduce image dimensions (512x512 recommended)
- Lower the batch size
- Enable model offloading in WebUI settings

**4. Model Not Found**
- Download a Stable Diffusion model
- Place it in `stable-diffusion-webui/models/Stable-diffusion/`
- Refresh models in WebUI

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [AUTOMATIC1111/stable-diffusion-webui](https://github.com/AUTOMATIC1111/stable-diffusion-webui)
- [Salesforce BLIP](https://github.com/salesforce/BLIP)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Hugging Face Transformers](https://huggingface.co/transformers/)

## 📞 Contact

If you have any questions or suggestions, please open an issue on GitHub.

---

⭐ Star this repository if you find it helpful!
