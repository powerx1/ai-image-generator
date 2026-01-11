document.getElementById("generate").addEventListener("click", async () => {
    const prompt = document.getElementById("prompt").value;
    const negative = document.getElementById("negative_prompt").value;
    const stepsEl = document.getElementById("steps");
    const cfgEl = document.getElementById("cfg_scale");
    const steps = stepsEl ? stepsEl.value : 30;
    const cfg = cfgEl ? cfgEl.value : 7;
    const width = document.getElementById("width").value;
    const height = document.getElementById("height").value;
    const sampler = document.getElementById("sampler_name").value;
    
    // Check for img2img specific elements
    const modeEl = document.getElementById("mode");
    const mode = modeEl ? modeEl.value : "txt2img";
    const initImageEl = document.getElementById("init_image");
    const denoisingEl = document.getElementById("denoising_strength");

    if (!prompt) {
        alert("اكتب prompt أولاً");
        return;
    }

    // For img2img mode, require an image
    if (mode === "img2img" && (!initImageEl || !initImageEl.files || initImageEl.files.length === 0)) {
        alert("Please upload an image for img2img mode");
        return;
    }

    toggleLoader(true);

    // Use ngrok URL when available, otherwise localhost
    const API_URL = 'https://unsinuous-mercedes-pseudopolitic.ngrok-free.dev';

    const formData = new FormData();
    formData.append("prompt", prompt);
    formData.append("negative_prompt", negative);
    formData.append("steps", steps);
    formData.append("cfg_scale", cfg);
    formData.append("width", width);
    formData.append("height", height);
    formData.append("sampler_name", sampler);
    formData.append("mode", mode);

    // Add img2img specific fields
    if (mode === "img2img") {
        if (initImageEl && initImageEl.files.length > 0) {
            formData.append("init_image", initImageEl.files[0]);
        }
        if (denoisingEl) {
            formData.append("denoising_strength", denoisingEl.value);
        }
    }

    try {
        console.log("Sending request with mode:", mode);
        console.log("FormData entries:");
        for (let [key, value] of formData.entries()) {
            if (key === "init_image") {
                console.log(key, ":", value.name, value.size, "bytes");
            } else {
                console.log(key, ":", value);
            }
        }

        const res = await fetch(`${API_URL}/generate`, {
            method: "POST",
            body: formData
        });

        const data = await res.json();
        console.log("Response:", data);

        if (data.image) {
            addImageToGallery(data.image);
        } else {
            alert(data.error || "فشل توليد الصورة");
        }
    } catch (e) {
        console.error("Error:", e);
        alert("خطأ في الاتصال بالـ API: " + e.message);
    } finally {
        toggleLoader(false);
    }
});

// Show/hide spinner
function toggleLoader(show) {
    const spinner = document.getElementById('spinner');
    if (!spinner) return;
    spinner.style.display = show ? 'block' : 'none';
}

// Add generated image (base64) to gallery
function addImageToGallery(base64) {
    const gallery = document.getElementById('gallery');
    if (!gallery) return;

    const empty = document.getElementById('empty');
    if (empty) empty.remove();

    const thumb = document.createElement('div');
    thumb.className = 'thumb';

    const img = document.createElement('img');
    img.src = 'data:image/png;base64,' + base64;
    img.alt = 'Generated image';
    thumb.appendChild(img);

    gallery.prepend(thumb);

    const downloadLink = document.getElementById('download_link');
    if (downloadLink) {
        downloadLink.href = img.src;
        downloadLink.style.display = 'inline';
        downloadLink.download = 'generated.png';
        downloadLink.textContent = 'Download';
    }
}

// Clear gallery
const clearBtn = document.getElementById('clear');
if (clearBtn) {
    clearBtn.addEventListener('click', () => {
        const gallery = document.getElementById('gallery');
        if (!gallery) return;
        gallery.innerHTML = '<div class="thumb" id="empty"><div class="meta">No images yet — generate one</div></div>';
        const downloadLink = document.getElementById('download_link');
        if (downloadLink) downloadLink.style.display = 'none';
    });
}

// Update range meta values
const stepsInput = document.getElementById('steps');
const stepsVal = document.getElementById('stepsVal');
if (stepsInput && stepsVal) {
    stepsInput.addEventListener('input', () => stepsVal.textContent = stepsInput.value);
}

const cfgInput = document.getElementById('cfg_scale');
const cfgVal = document.getElementById('cfgVal');
if (cfgInput && cfgVal) {
    cfgInput.addEventListener('input', () => cfgVal.textContent = cfgInput.value);
}
