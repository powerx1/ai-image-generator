"""
Cloud API Backend for AI Image Generator
Uses Replicate.com for Stable Diffusion (no local GPU needed)
"""
from fastapi import FastAPI, Form, UploadFile, File, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import base64
import httpx
from datetime import datetime
from typing import Optional
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Image Generator API", version="2.0")

# CORS - Allow all origins for demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Keys - Set these as environment variables
REPLICATE_API_TOKEN = os.environ.get("REPLICATE_API_TOKEN", "")

# Import database if available
try:
    import database
    DB_AVAILABLE = True
except ImportError:
    DB_AVAILABLE = False
    logger.warning("Database module not available")


@app.get("/")
def home():
    return {
        "status": "API running successfully",
        "version": "2.0 - Cloud Edition",
        "replicate_configured": bool(REPLICATE_API_TOKEN)
    }


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
    mode: str = Form("txt2img"),
    init_image: Optional[UploadFile] = File(None),
):
    """Generate image using Replicate API (Stable Diffusion in the cloud)"""
    
    if not REPLICATE_API_TOKEN:
        return JSONResponse(
            status_code=503,
            content={
                "error": "Replicate API not configured",
                "message": "Set REPLICATE_API_TOKEN environment variable",
                "demo_mode": True
            }
        )
    
    logger.info(f"Generating image - prompt: {prompt[:50]}...")
    
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            # Use Stable Diffusion XL on Replicate
            response = await client.post(
                "https://api.replicate.com/v1/predictions",
                headers={
                    "Authorization": f"Token {REPLICATE_API_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "version": "39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",  # SDXL
                    "input": {
                        "prompt": prompt,
                        "negative_prompt": negative_prompt,
                        "num_inference_steps": min(steps, 50),  # Cap at 50 for speed
                        "guidance_scale": cfg_scale,
                        "width": width,
                        "height": height,
                        "seed": seed if seed != -1 else None
                    }
                }
            )
            
            if response.status_code != 201:
                logger.error(f"Replicate API error: {response.text}")
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": "Failed to start generation", "details": response.text}
                )
            
            prediction = response.json()
            prediction_id = prediction["id"]
            
            # Poll for result
            for _ in range(60):  # Max 60 attempts (2 minutes)
                await asyncio.sleep(2)
                
                status_response = await client.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers={"Authorization": f"Token {REPLICATE_API_TOKEN}"}
                )
                
                result = status_response.json()
                
                if result["status"] == "succeeded":
                    output_url = result["output"][0] if result["output"] else None
                    
                    if output_url:
                        # Download the image and convert to base64
                        img_response = await client.get(output_url)
                        img_base64 = base64.b64encode(img_response.content).decode("utf-8")
                        
                        return {
                            "message": "Image generated successfully",
                            "image": img_base64,
                            "seed": result.get("seed", seed)
                        }
                
                elif result["status"] == "failed":
                    return JSONResponse(
                        status_code=500,
                        content={"error": "Generation failed", "details": result.get("error")}
                    )
            
            return JSONResponse(
                status_code=408,
                content={"error": "Generation timed out"}
            )
            
    except Exception as e:
        logger.exception(f"Error generating image: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.post("/img2text")
async def image_to_text(
    image: UploadFile = File(...),
    question: Optional[str] = Form(None),
):
    """Generate text description from image using Replicate API"""
    
    if not REPLICATE_API_TOKEN:
        return JSONResponse(
            status_code=503,
            content={"error": "Replicate API not configured"}
        )
    
    try:
        # Read and encode image
        img_bytes = await image.read()
        img_base64 = base64.b64encode(img_bytes).decode("utf-8")
        img_data_uri = f"data:image/png;base64,{img_base64}"
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            # Use BLIP on Replicate for image captioning
            response = await client.post(
                "https://api.replicate.com/v1/predictions",
                headers={
                    "Authorization": f"Token {REPLICATE_API_TOKEN}",
                    "Content-Type": "application/json"
                },
                json={
                    "version": "2e1dddc8621f72155f24cf2e0adbde548458d3cab9f00c0139eea840d0ac4746",  # BLIP
                    "input": {
                        "image": img_data_uri,
                        "task": "image_captioning" if not question else "visual_question_answering",
                        "question": question or ""
                    }
                }
            )
            
            if response.status_code != 201:
                return JSONResponse(
                    status_code=response.status_code,
                    content={"error": "Failed to start captioning"}
                )
            
            prediction = response.json()
            prediction_id = prediction["id"]
            
            # Poll for result
            import asyncio
            for _ in range(30):
                await asyncio.sleep(1)
                
                status_response = await client.get(
                    f"https://api.replicate.com/v1/predictions/{prediction_id}",
                    headers={"Authorization": f"Token {REPLICATE_API_TOKEN}"}
                )
                
                result = status_response.json()
                
                if result["status"] == "succeeded":
                    return {
                        "message": "Text generated successfully",
                        "text": result["output"],
                        "question": question
                    }
                elif result["status"] == "failed":
                    return JSONResponse(
                        status_code=500,
                        content={"error": "Captioning failed"}
                    )
            
            return JSONResponse(
                status_code=408,
                content={"error": "Captioning timed out"}
            )
            
    except Exception as e:
        logger.exception(f"Error in image-to-text: {e}")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


# =====================================================
# AUTHENTICATION ENDPOINTS (using local database)
# =====================================================

@app.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: Optional[str] = Form(None)
):
    """Register a new user"""
    if not DB_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={"success": False, "message": "Database not available"}
        )
    
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
):
    """Login a user and return session token"""
    if not DB_AVAILABLE:
        return JSONResponse(
            status_code=503,
            content={"success": False, "message": "Database not available"}
        )
    
    success, message, user_data = database.login_user(username, password)
    
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


# Add missing import at top
import asyncio


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
