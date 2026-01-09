// Image preview functionality
const inputImage = document.getElementById('input_image');
const imagePreview = document.getElementById('image-preview');
const previewContainer = document.getElementById('preview-container');
const clearImageBtn = document.getElementById('clear-image');

inputImage.addEventListener('change', (e) => {
    const file = e.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = (event) => {
            imagePreview.src = event.target.result;
            previewContainer.style.display = 'block';
        };
        reader.readAsDataURL(file);
    }
});

clearImageBtn.addEventListener('click', () => {
    inputImage.value = '';
    imagePreview.src = '';
    previewContainer.style.display = 'none';
});

// Max length slider
const maxLengthSlider = document.getElementById('max_length');
const maxLengthDisplay = document.getElementById('max_length_display');

maxLengthSlider.addEventListener('input', (e) => {
    maxLengthDisplay.textContent = e.target.value;
});

// Quick prompt buttons
const quickPromptButtons = document.querySelectorAll('.quick-prompt-btn');
const questionTextarea = document.getElementById('question');

quickPromptButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        const prompt = btn.getAttribute('data-prompt');
        questionTextarea.value = prompt;
        
        // Visual feedback
        quickPromptButtons.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
    });
});

// Loader functions
function toggleLoader(show) {
    const loader = document.getElementById('loader');
    const placeholder = document.getElementById('placeholder');
    const resultContent = document.getElementById('result-content');
    
    if (show) {
        loader.style.display = 'flex';
        placeholder.style.display = 'none';
        resultContent.style.display = 'none';
    } else {
        loader.style.display = 'none';
    }
}

function showResult(text, question) {
    const resultContent = document.getElementById('result-content');
    const resultText = document.getElementById('result-text');
    const resultQuestion = document.getElementById('result-question');
    const placeholder = document.getElementById('placeholder');
    
    resultText.textContent = text;
    resultQuestion.textContent = question;
    
    placeholder.style.display = 'none';
    resultContent.style.display = 'block';
}

// Copy text functionality
document.getElementById('copy-text').addEventListener('click', () => {
    const resultText = document.getElementById('result-text').textContent;
    navigator.clipboard.writeText(resultText).then(() => {
        const copyBtn = document.getElementById('copy-text');
        const originalHTML = copyBtn.innerHTML;
        
        copyBtn.innerHTML = '<i class="fas fa-check"></i><span>Copied!</span>';
        copyBtn.classList.add('success');
        
        setTimeout(() => {
            copyBtn.innerHTML = originalHTML;
            copyBtn.classList.remove('success');
        }, 2000);
    }).catch(err => {
        console.error('Failed to copy text:', err);
        alert('Failed to copy text to clipboard');
    });
});

// Main analyze function
document.getElementById('analyze').addEventListener('click', async () => {
    const imageFile = inputImage.files[0];
    const question = questionTextarea.value.trim() || "Describe this image in detail.";
    const maxLength = maxLengthSlider.value;
    
    if (!imageFile) {
        alert('Please upload an image first!');
        return;
    }
    
    toggleLoader(true);
    
    const formData = new FormData();
    formData.append('image', imageFile);
    formData.append('question', question);
    formData.append('max_length', maxLength);
    
    try {
        console.log('Sending image-to-text request...');
        console.log('Question:', question);
        console.log('Max length:', maxLength);
        
        const res = await fetch('http://127.0.0.1:8000/image-to-text', {
            method: 'POST',
            body: formData
        });
        
        const data = await res.json();
        console.log('Response:', data);
        
        if (data.text) {
            showResult(data.text, data.question);
        } else if (data.error) {
            alert('Error: ' + data.error);
            console.error('API Error:', data.error);
        } else {
            alert('Failed to analyze image. No text returned.');
        }
    } catch (e) {
        console.error('Error:', e);
        alert('Connection error: ' + e.message);
    } finally {
        toggleLoader(false);
    }
});

// Drag and drop functionality
const fileUploadLabel = document.querySelector('.file-upload-label');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    fileUploadLabel.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    fileUploadLabel.addEventListener(eventName, () => {
        fileUploadLabel.classList.add('drag-over');
    });
});

['dragleave', 'drop'].forEach(eventName => {
    fileUploadLabel.addEventListener(eventName, () => {
        fileUploadLabel.classList.remove('drag-over');
    });
});

fileUploadLabel.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    
    if (files.length > 0) {
        inputImage.files = files;
        inputImage.dispatchEvent(new Event('change'));
    }
});
