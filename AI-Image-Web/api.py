from fastapi import FastAPI, Form, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import requests
import base64
import os
from datetime import datetime
from typing import Optional
import logging
from PIL import Image
import io
import database

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Initialize BLIP model (lazy loading) - lighter and faster than MiniCPM-o
blip_model = None
blip_processor = None

def load_blip_model():
    """Load BLIP model for image-to-text (lighter, works well on CPU)."""
    global blip_model, blip_processor
    if blip_model is None:
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            import torch
            
            logger.info("Loading BLIP model...")
            model_name = "Salesforce/blip-image-captioning-large"
            
            blip_processor = BlipProcessor.from_pretrained(model_name)
            blip_model = BlipForConditionalGeneration.from_pretrained(model_name)
            
            # Move to GPU if available
            if torch.cuda.is_available():
                blip_model = blip_model.cuda()
                logger.info("BLIP model loaded on GPU")
            else:
                logger.info("BLIP model loaded on CPU")
            
            blip_model.eval()
            logger.info("BLIP model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load BLIP model: {e}")
            raise
    
    return blip_model, blip_processor

# السماح للاتصال من الواجهة Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

STABLE_URL = os.environ.get("STABLE_URL", "http://127.0.0.1:7861")  # رابط WebUI (default 7860; override with env STABLE_URL)

@app.get("/")
def home():
    return {"status": "API running successfully"}

@app.post("/generate")
async def generate_image(
    prompt: str = Form(...),
    negative_prompt: str = Form(""),
    steps: int = Form(30),
    cfg_scale: float = Form(7.0),
    width: int = Form(512),
    height: int = Form(512),
    sampler_name: str = Form("DPM++ 2M Karras"),
    seed: int = Form(-1),
    batch_size: int = Form(1),
    n_iter: int = Form(1),
    mode: str = Form("txt2img"),
    denoising_strength: float = Form(0.75),
    init_image: Optional[UploadFile] = File(None),
):
    """Generate image via Stable Diffusion WebUI API.
    Accepts form fields from the frontend and forwards them to the webui.
    """
    logger.info(f"Received request - mode: {mode}, prompt: {prompt[:50]}...")
    logger.info(f"init_image: {init_image}")
    
    try:
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": int(steps),
            "cfg_scale": float(cfg_scale),
            "width": int(width),
            "height": int(height),
            "sampler_name": sampler_name,
            "seed": int(seed),
            "batch_size": int(batch_size),
            "n_iter": int(n_iter),
        }

        # Prepare endpoint and payload for img2img if requested
        if mode == 'img2img':
            endpoint = f"{STABLE_URL}/sdapi/v1/img2img"
            payload["denoising_strength"] = float(denoising_strength)

            if init_image is not None:
                img_bytes = await init_image.read()
                logger.info(f"Read {len(img_bytes)} bytes from init_image")
                b64 = base64.b64encode(img_bytes).decode('utf-8')
                # SD WebUI accepts plain base64 strings for init_images
                payload["init_images"] = [b64]
                logger.info(f"Added init_images to payload, base64 length: {len(b64)}")
            else:
                logger.error("img2img mode but no init_image provided")
                return {"error": "img2img mode requires an init image"}
        else:
            endpoint = f"{STABLE_URL}/sdapi/v1/txt2img"

        # Forward request to Stable Diffusion WebUI
        logger.info(f"Sending request to {endpoint}")
        res = requests.post(endpoint, json=payload, timeout=120)
        logger.info(f"Response status: {res.status_code}")
        
        if not res.ok:
            logger.error(f"Stable WebUI error: {res.status_code} {res.text}")
            return {"error": f"Stable WebUI error: {res.status_code} {res.text}"}

        data = res.json()
        if not data or "images" not in data or len(data["images"]) == 0:
            logger.error("No image returned from Stable WebUI")
            return {"error": "No image returned from Stable WebUI"}

        img_base64 = data["images"][0]
        logger.info(f"Received image, base64 length: {len(img_base64)}")

        # save locally
        os.makedirs("output", exist_ok=True)
        file_name = f"output/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        with open(file_name, "wb") as f:
            f.write(base64.b64decode(img_base64))

        logger.info(f"Image saved to {file_name}")
        return {
            "message": "Image generated successfully",
            "image": img_base64,
            "file": file_name,
        }

    except Exception as e:
        logger.exception(f"Error generating image: {e}")
        return {"error": str(e)}


@app.post("/image-to-text")
async def image_to_text(
    image: UploadFile = File(...),
    question: str = Form("Describe this image in detail."),
    max_length: int = Form(512),
):
    """Generate text description from an image using BLIP model.
    
    Args:
        image: The image file to analyze
        question: The question or prompt for the model (used as conditional text)
        max_length: Maximum length of generated text
    
    Returns:
        JSON with the generated text description
    """
    logger.info(f"Received image-to-text request with question: {question[:50]}...")
    
    try:
        # Load model (lazy loading)
        model, processor = load_blip_model()
        
        # Read and process the image
        img_bytes = await image.read()
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        logger.info(f"Image loaded: {img.size}")
        
        import torch
        
        # BLIP supports both unconditional and conditional captioning
        # If question is a generic "describe", use unconditional captioning
        # Otherwise, use the question as conditional text
        generic_prompts = ["describe this image", "what is in this image", "describe"]
        is_generic = any(p in question.lower() for p in generic_prompts)
        
        with torch.no_grad():
            if is_generic:
                # Unconditional image captioning
                inputs = processor(img, return_tensors="pt")
                if torch.cuda.is_available():
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                
                output_ids = model.generate(**inputs, max_length=max_length)
                response = processor.decode(output_ids[0], skip_special_tokens=True)
            else:
                # Conditional image captioning (with prompt/question)
                inputs = processor(img, question, return_tensors="pt")
                if torch.cuda.is_available():
                    inputs = {k: v.cuda() for k, v in inputs.items()}
                
                output_ids = model.generate(**inputs, max_length=max_length)
                response = processor.decode(output_ids[0], skip_special_tokens=True)
        
        logger.info(f"Generated text: {response[:100]}...")
        
        return {
            "message": "Text generated successfully",
            "text": response,
            "question": question
        }
        
    except Exception as e:
        logger.exception(f"Error in image-to-text: {e}")
        return {"error": str(e)}


# =====================================================
# AUTHENTICATION ENDPOINTS
# =====================================================

@app.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: Optional[str] = Form(None)
):
    """Register a new user"""
    if len(password) < 6:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Password must be at least 6 characters"}
        )
    
    success, message = database.register_user(username, email, password, full_name)
    
    if success:
        return {"success": True, "message": message}
    else:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": message}
        )


@app.post("/login")
async def login(
    username: str = Form(...),
    password: str = Form(...),
    user_agent: Optional[str] = Header(None)
):
    """Login a user and return session token"""
    success, message, user_data = database.login_user(
        username, password, user_agent=user_agent
    )
    
    if success:
        return {
            "success": True,
            "message": message,
            "user": user_data
        }
    else:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": message}
        )


@app.post("/logout")
async def logout(authorization: Optional[str] = Header(None)):
    """Logout a user by invalidating their session"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session_token = authorization.replace("Bearer ", "")
    success = database.logout_user(session_token)
    
    if success:
        return {"success": True, "message": "Logged out successfully"}
    else:
        return JSONResponse(
            status_code=400,
            content={"success": False, "message": "Logout failed"}
        )


@app.get("/verify")
async def verify_session(authorization: Optional[str] = Header(None)):
    """Verify if a session token is valid"""
    if not authorization or not authorization.startswith("Bearer "):
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Not authenticated"}
        )
    
    session_token = authorization.replace("Bearer ", "")
    valid, user_data = database.verify_session(session_token)
    
    if valid:
        return {"success": True, "user": user_data}
    else:
        return JSONResponse(
            status_code=401,
            content={"success": False, "message": "Invalid or expired session"}
        )


@app.get("/my-images")
async def get_my_images(authorization: Optional[str] = Header(None)):
    """Get the current user's generated images"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    session_token = authorization.replace("Bearer ", "")
    valid, user_data = database.verify_session(session_token)
    
    if not valid:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    images = database.get_user_images(user_data['id'])
    return {"success": True, "images": images}
