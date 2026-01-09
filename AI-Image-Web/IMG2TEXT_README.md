# MiniCPM-o Image-to-Text Feature

## Overview
I've successfully added MiniCPM-o image-to-text functionality to your AI Image Web application. This feature allows users to upload images and get AI-generated text descriptions powered by the MiniCPM-o multimodal model.

## What Was Added

### 1. **Backend API Endpoint** (`api.py`)
- New `/image-to-text` POST endpoint
- Lazy loading of MiniCPM-o model (loads only when first used)
- Supports custom questions/prompts for image analysis
- Configurable max text length

### 2. **Frontend Page** (`img2text.html`)
- Beautiful, modern UI matching your existing design
- Image upload with preview
- Quick prompt buttons for common questions
- Adjustable max length slider
- Real-time text generation results
- Copy-to-clipboard functionality

### 3. **JavaScript** (`img2text.js`)
- Handles image upload and preview
- Drag-and-drop support
- Quick prompt selection
- API communication
- Result display and copying

### 4. **Styles** (`img2text-styles.css`)
- Consistent with your existing design
- Glass morphism and aurora effects
- Fully responsive
- Smooth animations

### 5. **Navigation Updates**
- Added "Img2Text" link to all pages
- Consistent navigation across Txt2Img, Img2Img, and Img2Text pages

## How to Use

### 1. Install Dependencies
First, install the new Python packages required for MiniCPM-o:

```bash
# Activate your virtual environment
.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r AI-Image-Web\requirements.txt
```

**Note:** The MiniCPM-o model download will happen automatically on first use. It's approximately 5-7 GB, so ensure you have:
- Sufficient disk space
- Good internet connection
- Time for the initial download (only needed once)

### 2. Start the FastAPI Server
```bash
uvicorn AI-Image-Web.api:app --host 0.0.0.0 --port 8000 --reload
```

### 3. Start the Static File Server
```bash
python AI-Image-Web\serve.py 5500
```

### 4. Access the Feature
Open your browser and go to:
- **Main site:** http://localhost:5500/index.html
- **Img2Text page:** http://localhost:5500/img2text.html

## Features

### Image Upload
- **Drag & Drop:** Simply drag an image onto the upload area
- **Click to Upload:** Click the upload area to browse for images
- **Supported Formats:** JPG, PNG, WEBP
- **Preview:** See your uploaded image before analysis

### Custom Questions
You can ask specific questions about the image:
- **Describe:** Get a detailed description
- **Objects:** Identify objects in the image
- **Subject:** Find the main subject
- **Mood:** Analyze emotions and mood
- **Custom:** Type your own question

### Results
- **Real-time Analysis:** See the AI's text generation
- **Copy to Clipboard:** One-click copying of results
- **Question Context:** View what question was asked

## API Usage

### Endpoint: `/image-to-text`
**Method:** POST  
**Content-Type:** multipart/form-data

**Parameters:**
- `image` (file, required): The image file to analyze
- `question` (string, optional): Question or prompt for the model  
  Default: "Describe this image in detail."
- `max_length` (int, optional): Maximum length of generated text  
  Default: 512

**Example using curl:**
```bash
curl -X POST "http://127.0.0.1:8000/image-to-text" \
  -F "image=@path/to/your/image.jpg" \
  -F "question=What objects are in this image?" \
  -F "max_length=512"
```

**Response:**
```json
{
  "message": "Text generated successfully",
  "text": "The image shows a golden retriever dog sitting in a sunny park...",
  "question": "What objects are in this image?"
}
```

## Performance Notes

### First Use
- The model will download automatically (5-7 GB)
- First request may take 30-60 seconds as model loads into memory
- Subsequent requests are much faster (2-5 seconds depending on hardware)

### GPU Acceleration
- If you have an NVIDIA GPU with CUDA, the model will automatically use it
- This significantly speeds up inference (2-3x faster)
- CPU-only mode works but is slower

### Memory Requirements
- Minimum 8 GB RAM
- Recommended 16 GB RAM
- GPU with 6+ GB VRAM (optional but recommended)

## Troubleshooting

### Model Download Issues
If the model fails to download:
```python
# Manually download using Python
from transformers import AutoModel, AutoTokenizer
model_name = "openbmb/MiniCPM-o-2_6"
AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
AutoModel.from_pretrained(model_name, trust_remote_code=True)
```

### CUDA Out of Memory
If you get CUDA out of memory errors:
1. Reduce `max_length` parameter
2. Close other GPU-intensive applications
3. Force CPU mode by setting `CUDA_VISIBLE_DEVICES=-1`

### Slow Performance
- Ensure you're using GPU if available
- Reduce `max_length` for faster generation
- Consider using a smaller model variant if available

## Model Information

**MiniCPM-o** is a powerful multimodal model that can:
- Understand and analyze images
- Answer questions about visual content
- Generate detailed descriptions
- Identify objects, scenes, and concepts
- Understand context and relationships in images

**Version:** MiniCPM-o-2.6  
**Provider:** OpenBMB  
**License:** Check the model's license on HuggingFace

## Future Enhancements

Potential improvements:
- Batch image processing
- Image comparison (compare two images)
- OCR text extraction
- Image captioning presets
- Result history
- Export results to file

## Files Added/Modified

**New Files:**
- `AI-Image-Web/img2text.html` - Main image-to-text page
- `AI-Image-Web/img2text.js` - Frontend logic
- `AI-Image-Web/img2text-styles.css` - Styles for the page
- `AI-Image-Web/IMG2TEXT_README.md` - This file

**Modified Files:**
- `AI-Image-Web/api.py` - Added `/image-to-text` endpoint
- `AI-Image-Web/requirements.txt` - Added new dependencies
- `AI-Image-Web/index.html` - Updated navigation
- `AI-Image-Web/img2img.html` - Updated navigation

## Need Help?

If you encounter any issues:
1. Check the FastAPI logs for errors
2. Ensure all dependencies are installed
3. Verify the model downloaded successfully
4. Check your internet connection for first-time use
5. Monitor GPU/CPU usage during inference

Enjoy your new image-to-text feature! 🎉
