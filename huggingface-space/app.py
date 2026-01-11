"""
AI Image Generator - Hugging Face Spaces Version
Uses Gradio interface for easy deployment
"""
import gradio as gr
import torch
from diffusers import StableDiffusionPipeline, StableDiffusionImg2ImgPipeline
from PIL import Image
import os

# Model configuration
MODEL_ID = "runwayml/stable-diffusion-v1-5"  # Free model, no license needed
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# Load models (lazy loading)
txt2img_pipe = None
img2img_pipe = None

def load_txt2img():
    global txt2img_pipe
    if txt2img_pipe is None:
        print("Loading text-to-image model...")
        txt2img_pipe = StableDiffusionPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            safety_checker=None
        )
        txt2img_pipe = txt2img_pipe.to(DEVICE)
        if DEVICE == "cuda":
            txt2img_pipe.enable_attention_slicing()
    return txt2img_pipe

def load_img2img():
    global img2img_pipe
    if img2img_pipe is None:
        print("Loading image-to-image model...")
        img2img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            MODEL_ID,
            torch_dtype=torch.float16 if DEVICE == "cuda" else torch.float32,
            safety_checker=None
        )
        img2img_pipe = img2img_pipe.to(DEVICE)
        if DEVICE == "cuda":
            img2img_pipe.enable_attention_slicing()
    return img2img_pipe


def generate_txt2img(prompt, negative_prompt, steps, guidance_scale, width, height, seed):
    """Generate image from text prompt"""
    if not prompt:
        return None, "Please enter a prompt"
    
    try:
        pipe = load_txt2img()
        
        generator = None
        if seed != -1:
            generator = torch.Generator(DEVICE).manual_seed(seed)
        
        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            num_inference_steps=int(steps),
            guidance_scale=guidance_scale,
            width=int(width),
            height=int(height),
            generator=generator
        )
        
        image = result.images[0]
        return image, f"✅ Generated successfully! Seed: {seed if seed != -1 else 'random'}"
    
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


def generate_img2img(init_image, prompt, negative_prompt, steps, guidance_scale, strength, seed):
    """Transform image with text prompt"""
    if init_image is None:
        return None, "Please upload an image"
    if not prompt:
        return None, "Please enter a prompt"
    
    try:
        pipe = load_img2img()
        
        # Resize image
        init_image = init_image.convert("RGB")
        init_image = init_image.resize((512, 512))
        
        generator = None
        if seed != -1:
            generator = torch.Generator(DEVICE).manual_seed(seed)
        
        result = pipe(
            prompt=prompt,
            negative_prompt=negative_prompt,
            image=init_image,
            num_inference_steps=int(steps),
            guidance_scale=guidance_scale,
            strength=strength,
            generator=generator
        )
        
        image = result.images[0]
        return image, f"✅ Generated successfully!"
    
    except Exception as e:
        return None, f"❌ Error: {str(e)}"


# Create Gradio Interface
with gr.Blocks(title="AI Image Generator", theme=gr.themes.Soft()) as demo:
    gr.Markdown("""
    # 🎨 AI Image Generator
    ### Generate stunning images with Stable Diffusion
    **Created by Hasan Abonaaj** | [GitHub](https://github.com/powerx1/ai-image-generator)
    """)
    
    with gr.Tabs():
        # Text to Image Tab
        with gr.TabItem("🖼️ Text to Image"):
            with gr.Row():
                with gr.Column(scale=1):
                    txt2img_prompt = gr.Textbox(
                        label="Prompt",
                        placeholder="A beautiful sunset over mountains, digital art, highly detailed",
                        lines=3
                    )
                    txt2img_negative = gr.Textbox(
                        label="Negative Prompt",
                        placeholder="blurry, bad quality, distorted",
                        lines=2
                    )
                    
                    with gr.Row():
                        txt2img_steps = gr.Slider(10, 50, value=25, step=1, label="Steps")
                        txt2img_cfg = gr.Slider(1, 20, value=7.5, step=0.5, label="CFG Scale")
                    
                    with gr.Row():
                        txt2img_width = gr.Dropdown([256, 512, 768], value=512, label="Width")
                        txt2img_height = gr.Dropdown([256, 512, 768], value=512, label="Height")
                    
                    txt2img_seed = gr.Number(value=-1, label="Seed (-1 for random)")
                    txt2img_btn = gr.Button("🎨 Generate", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    txt2img_output = gr.Image(label="Generated Image", type="pil")
                    txt2img_status = gr.Textbox(label="Status", interactive=False)
            
            txt2img_btn.click(
                generate_txt2img,
                inputs=[txt2img_prompt, txt2img_negative, txt2img_steps, txt2img_cfg, txt2img_width, txt2img_height, txt2img_seed],
                outputs=[txt2img_output, txt2img_status]
            )
        
        # Image to Image Tab
        with gr.TabItem("🔄 Image to Image"):
            with gr.Row():
                with gr.Column(scale=1):
                    img2img_input = gr.Image(label="Upload Image", type="pil")
                    img2img_prompt = gr.Textbox(
                        label="Prompt",
                        placeholder="Transform into a watercolor painting",
                        lines=3
                    )
                    img2img_negative = gr.Textbox(
                        label="Negative Prompt",
                        placeholder="blurry, bad quality",
                        lines=2
                    )
                    
                    with gr.Row():
                        img2img_steps = gr.Slider(10, 50, value=25, step=1, label="Steps")
                        img2img_cfg = gr.Slider(1, 20, value=7.5, step=0.5, label="CFG Scale")
                    
                    img2img_strength = gr.Slider(0.1, 1.0, value=0.75, step=0.05, label="Strength")
                    img2img_seed = gr.Number(value=-1, label="Seed (-1 for random)")
                    img2img_btn = gr.Button("🔄 Transform", variant="primary", size="lg")
                
                with gr.Column(scale=1):
                    img2img_output = gr.Image(label="Transformed Image", type="pil")
                    img2img_status = gr.Textbox(label="Status", interactive=False)
            
            img2img_btn.click(
                generate_img2img,
                inputs=[img2img_input, img2img_prompt, img2img_negative, img2img_steps, img2img_cfg, img2img_strength, img2img_seed],
                outputs=[img2img_output, img2img_status]
            )
    
    gr.Markdown("""
    ---
    ### 💡 Tips
    - Use descriptive prompts for better results
    - Add style keywords like "digital art", "oil painting", "photorealistic"
    - Use negative prompts to avoid unwanted features
    - Lower steps = faster but lower quality | Higher steps = slower but better quality
    
    ### ⚠️ Note
    Running on CPU may be slow. For faster generation, duplicate this space with GPU!
    """)


# Launch
if __name__ == "__main__":
    demo.launch()
