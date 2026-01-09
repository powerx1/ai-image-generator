from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import base64
import os
from datetime import datetime
from PIL import Image
import io

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

STABLE_URL = os.environ.get("STABLE_URL", "http://0.0.0.0:7861")

# Initialize BLIP model (lazy loading) - lighter and faster
blip_model = None
blip_processor = None

def load_blip_model():
    """Load BLIP model for image-to-text (lighter, works well on CPU)."""
    global blip_model, blip_processor
    if blip_model is None:
        try:
            from transformers import BlipProcessor, BlipForConditionalGeneration
            import torch
            
            print("Loading BLIP model...")
            model_name = "Salesforce/blip-image-captioning-large"
            
            blip_processor = BlipProcessor.from_pretrained(model_name)
            blip_model = BlipForConditionalGeneration.from_pretrained(model_name)
            
            # Move to GPU if available
            if torch.cuda.is_available():
                blip_model = blip_model.cuda()
                print("BLIP model loaded on GPU")
            else:
                print("BLIP model loaded on CPU")
            
            blip_model.eval()
            print("BLIP model loaded successfully")
        except Exception as e:
            print(f"Failed to load BLIP model: {e}")
            raise
    
    return blip_model, blip_processor

@app.route("/")
def home():
    return jsonify({"status": "API running successfully"})

@app.route("/generate", methods=["POST"])
def generate_image():
    """Generate image via Stable Diffusion WebUI API."""
    try:
        # Get form data
        prompt = request.form.get("prompt", "")
        negative_prompt = request.form.get("negative_prompt", "")
        steps = int(request.form.get("steps", 30))
        cfg_scale = float(request.form.get("cfg_scale", 7.0))
        width = int(request.form.get("width", 512))
        height = int(request.form.get("height", 512))
        sampler_name = request.form.get("sampler_name", "DPM++ 2M Karras")
        seed = int(request.form.get("seed", -1))
        batch_size = int(request.form.get("batch_size", 1))
        n_iter = int(request.form.get("n_iter", 1))
        mode = request.form.get("mode", "txt2img")
        denoising_strength = float(request.form.get("denoising_strength", 0.75))

        print(f"Received request - mode: {mode}, prompt: {prompt[:50]}...")

        # Build payload
        payload = {
            "prompt": prompt,
            "negative_prompt": negative_prompt,
            "steps": steps,
            "cfg_scale": cfg_scale,
            "width": width,
            "height": height,
            "sampler_name": sampler_name,
            "seed": seed,
            "batch_size": batch_size,
            "n_iter": n_iter,
        }

        # Handle img2img mode
        if mode == "img2img":
            endpoint = f"{STABLE_URL}/sdapi/v1/img2img"
            payload["denoising_strength"] = denoising_strength

            # Get uploaded image
            if "init_image" in request.files:
                init_image = request.files["init_image"]
                if init_image.filename:
                    img_bytes = init_image.read()
                    print(f"Read {len(img_bytes)} bytes from init_image")
                    b64 = base64.b64encode(img_bytes).decode("utf-8")
                    payload["init_images"] = [b64]
                    print(f"Added init_images to payload, base64 length: {len(b64)}")
                else:
                    return jsonify({"error": "img2img mode requires an init image"})
            else:
                return jsonify({"error": "img2img mode requires an init image"})
        else:
            endpoint = f"{STABLE_URL}/sdapi/v1/txt2img"

        # Forward request to Stable Diffusion WebUI
        print(f"Sending request to {endpoint}")
        res = requests.post(endpoint, json=payload, timeout=120)
        print(f"Response status: {res.status_code}")

        if not res.ok:
            print(f"Stable WebUI error: {res.status_code} {res.text}")
            return jsonify({"error": f"Stable WebUI error: {res.status_code} {res.text}"})

        data = res.json()
        if not data or "images" not in data or len(data["images"]) == 0:
            print("No image returned from Stable WebUI")
            return jsonify({"error": "No image returned from Stable WebUI"})

        img_base64 = data["images"][0]
        print(f"Received image, base64 length: {len(img_base64)}")

        # Save locally
        os.makedirs("output", exist_ok=True)
        file_name = f"output/{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        with open(file_name, "wb") as f:
            f.write(base64.b64decode(img_base64))

        print(f"Image saved to {file_name}")
        return jsonify({
            "message": "Image generated successfully",
            "image": img_base64,
            "file": file_name,
        })

    except Exception as e:
        print(f"Error generating image: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)})

@app.route("/image-to-text", methods=["POST"])
def image_to_text():
    """Generate text description from an image using BLIP model."""
    try:
        # Get the uploaded image
        if "image" not in request.files:
            return jsonify({"error": "No image file provided"})
        
        image_file = request.files["image"]
        if image_file.filename == "":
            return jsonify({"error": "No image file selected"})
        
        question = request.form.get("question", "Describe this image in detail.")
        max_length = int(request.form.get("max_length", 512))
        
        print(f"Received image-to-text request with question: {question[:50]}...")
        
        # Load model (lazy loading)
        model, processor = load_blip_model()
        
        # Read and process the image
        img_bytes = image_file.read()
        img = Image.open(io.BytesIO(img_bytes)).convert('RGB')
        print(f"Image loaded: {img.size}")
        
        import torch
        
        # BLIP supports both unconditional and conditional captioning
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
        
        print(f"Generated text: {response[:100]}...")
        
        return jsonify({
            "message": "Text generated successfully",
            "text": response,
            "question": question
        })
        
    except Exception as e:
        print(f"Error in image-to-text: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)})

if __name__ == "__main__":
    print(f"Starting server... STABLE_URL={STABLE_URL}")
    app.run(host="0.0.0.0", port=8000, debug=True)
