// =====================================================
// AUTHENTICATION FUNCTIONALITY
// =====================================================

document.addEventListener('DOMContentLoaded', () => {
    // Initialize authentication functionality
    initPasswordToggles();
    initPasswordStrength();
    initFormValidation();
    initSocialLogin();
});

// =====================================================
// PASSWORD TOGGLE
// =====================================================

function initPasswordToggles() {
    const toggleButtons = document.querySelectorAll('.toggle-password');
    
    toggleButtons.forEach(button => {
        button.addEventListener('click', () => {
            const wrapper = button.closest('.password-input-wrapper');
            const input = wrapper.querySelector('input');
            const icon = button.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
                button.classList.add('active');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
                button.classList.remove('active');
            }
        });
    });
}

// =====================================================
// PASSWORD STRENGTH INDICATOR
// =====================================================

function initPasswordStrength() {
    const passwordInput = document.getElementById('password');
    const strengthIndicator = document.getElementById('passwordStrength');
    
    if (!passwordInput || !strengthIndicator) return;
    
    const strengthBar = strengthIndicator.querySelector('.strength-bar');
    const strengthText = strengthIndicator.querySelector('.strength-text');
    
    passwordInput.addEventListener('input', () => {
        const password = passwordInput.value;
        const strength = calculatePasswordStrength(password);
        
        strengthBar.setAttribute('data-strength', strength.level);
        strengthText.textContent = strength.text;
    });
}

function calculatePasswordStrength(password) {
    let score = 0;
    
    if (!password) {
        return { level: 'weak', text: 'Password strength' };
    }
    
    // Length
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    
    // Character variety
    if (/[a-z]/.test(password)) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^a-zA-Z0-9]/.test(password)) score++;
    
    // Determine strength level
    if (score <= 2) {
        return { level: 'weak', text: 'Weak password' };
    } else if (score <= 4) {
        return { level: 'medium', text: 'Medium password' };
    } else {
        return { level: 'strong', text: 'Strong password' };
    }
}

// =====================================================
// FORM VALIDATION
// =====================================================

function initFormValidation() {
    const loginForm = document.getElementById('loginForm');
    const signupForm = document.getElementById('signupForm');
    
    if (loginForm) {
        loginForm.addEventListener('submit', handleLogin);
    }
    
    if (signupForm) {
        signupForm.addEventListener('submit', handleSignup);
    }
}

async function handleLogin(e) {
    e.preventDefault();
    
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const remember = document.getElementById('remember').checked;
    
    // Validate
    if (!email || email.length < 3) {
        showError('email', 'Please enter a valid username or email');
        return;
    }
    
    if (password.length < 6) {
        showError('password', 'Password must be at least 6 characters');
        return;
    }
    
    // Show loading state
    const form = e.target;
    form.classList.add('loading');
    const submitBtn = form.querySelector('.btn-primary');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Signing in...';
    
    try {
        // Try API call to login endpoint
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);
        
        // Check if backend is available - use ngrok URL for public access
        const API_URL = 'https://unsinuous-mercedes-pseudopolitic.ngrok-free.dev';
        
        try {
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                body: formData,
                signal: AbortSignal.timeout(3000) // 3 second timeout
            });
            
            const data = await response.json();
            
            if (data.success && data.user && data.user.session_token) {
                // Store auth token
                const storage = remember ? localStorage : sessionStorage;
                storage.setItem('session_token', data.user.session_token);
                storage.setItem('username', data.user.username);
                storage.setItem('email', data.user.email);
                
                // Show success
                showNotification('Login successful! Redirecting...', 'success');
                
                // Redirect
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1000);
                return;
            } else {
                throw new Error(data.message || 'Login failed');
            }
        } catch (apiError) {
            // Backend not available - use demo mode
            console.log('Backend not available, using demo mode:', apiError.message);
            
            // Show info message about demo mode
            showNotification('Backend unavailable - Using Demo Mode', 'info');
            
            // Check if user exists in localStorage (demo registration)
            const users = JSON.parse(localStorage.getItem('demo_users') || '{}');
            
            // Demo accounts
            if (email === 'demo' && password === 'demo123') {
                const storage = remember ? localStorage : sessionStorage;
                storage.setItem('session_token', 'demo-' + Date.now());
                storage.setItem('username', 'demo');
                storage.setItem('email', 'demo@example.com');
                storage.setItem('demo_mode', 'true');
                
                showNotification('Login successful (Demo Mode)! Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1000);
                return;
            }
            
            // Check registered demo users
            const userKey = Object.keys(users).find(key => 
                (users[key].username === email || users[key].email === email) && 
                users[key].password === password
            );
            
            if (userKey) {
                const storage = remember ? localStorage : sessionStorage;
                storage.setItem('session_token', 'demo-' + Date.now());
                storage.setItem('username', users[userKey].username);
                storage.setItem('email', users[userKey].email);
                storage.setItem('demo_mode', 'true');
                
                showNotification('Login successful (Demo Mode)! Redirecting...', 'success');
                setTimeout(() => {
                    window.location.href = 'index.html';
                }, 1000);
                return;
            }
            
            throw new Error('Invalid credentials. Try: username "demo" password "demo123"');
        }
        
    } catch (error) {
        showNotification(error.message || 'Login failed. Please check your credentials.', 'error');
        form.classList.remove('loading');
        submitBtn.innerHTML = originalText;
    }
}

async function handleSignup(e) {
    e.preventDefault();
    
    const firstName = document.getElementById('firstName').value;
    const lastName = document.getElementById('lastName').value;
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const terms = document.getElementById('terms').checked;
    
    // Enhanced Validation
    if (!firstName || !firstName.trim()) {
        showNotification('❌ First name is required', 'error');
        return;
    }
    
    if (!lastName || !lastName.trim()) {
        showNotification('❌ Last name is required', 'error');
        return;
    }
    
    if (!email || !email.trim()) {
        showNotification('❌ Email address is required', 'error');
        return;
    }
    
    if (!validateEmail(email)) {
        showError('email', '❌ Please enter a valid email address');
        return;
    }
    
    if (!password || password.length === 0) {
        showNotification('❌ Password is required', 'error');
        return;
    }
    
    if (password.length < 8) {
        showError('password', '❌ Password must be at least 8 characters');
        return;
    }
    
    if (!confirmPassword || confirmPassword.length === 0) {
        showNotification('❌ Please confirm your password', 'error');
        return;
    }
    
    if (password !== confirmPassword) {
        showError('confirmPassword', '❌ Passwords do not match');
        return;
    }
    
    if (!terms) {
        showNotification('❌ Please accept the terms of service', 'error');
        return;
    }
    
    // Show loading state
    const form = e.target;
    form.classList.add('loading');
    const submitBtn = form.querySelector('.btn-primary');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Creating account...';
    
    try {
        // Generate username from email
        const username = email.split('@')[0].toLowerCase();
        const fullName = `${firstName.trim()} ${lastName.trim()}`;
        
        // Check if backend is available - use ngrok URL for public access
        const API_URL = 'https://unsinuous-mercedes-pseudopolitic.ngrok-free.dev';
        
        try {
            // API call to register endpoint
            const formData = new FormData();
            formData.append('username', username);
            formData.append('email', email);
            formData.append('password', password);
            formData.append('full_name', fullName);
            
            const response = await fetch(`${API_URL}/register`, {
                method: 'POST',
                body: formData,
                signal: AbortSignal.timeout(3000)
            });
            
            const data = await response.json();
            
            if (data.success) {
                showNotification('Account created successfully! Redirecting to login...', 'success');
                setTimeout(() => {
                    window.location.href = 'login.html';
                }, 1500);
                return;
            } else {
                throw new Error(data.message || 'Registration failed');
            }
        } catch (apiError) {
            // Backend not available - use demo mode
            console.log('Backend not available, using demo registration');
            
            // Store in localStorage for demo
            const users = JSON.parse(localStorage.getItem('demo_users') || '{}');
            
            // Prevent empty email or password from being stored
            if (!email || !email.trim() || !password || !password.trim()) {
                throw new Error('❌ Email and password cannot be empty');
            }
            
            // Check if user already exists
            if (users[email] || Object.values(users).some(u => u.username === username)) {
                throw new Error('❌ Username or email already exists (Demo Mode)');
            }
            
            // Validate email format before storing
            if (!validateEmail(email)) {
                throw new Error('❌ Invalid email format');
            }
            
            // Save user in demo mode with validation
            users[email] = {
                username: username,
                email: email.trim(),
                password: password, // In demo mode only (not secure for production!)
                fullName: fullName.trim(),
                createdAt: new Date().toISOString()
            };
            
            localStorage.setItem('demo_users', JSON.stringify(users));
            
            // Log for debugging
            console.log('Demo user registered:', { username, email: email.trim(), fullName });
            
            showNotification('✅ Account created successfully (Demo Mode)! Redirecting to login...', 'success');
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1500);
        }
        
    } catch (error) {
        showNotification(error.message || 'Registration failed. Please try again.', 'error');
        form.classList.remove('loading');
        submitBtn.innerHTML = originalText;
    }
}

// =====================================================
// SOCIAL LOGIN
// =====================================================

function initSocialLogin() {
    const socialButtons = document.querySelectorAll('.btn-social');
    
    socialButtons.forEach(button => {
        button.addEventListener('click', async () => {
            const provider = button.textContent.trim().toLowerCase();
            
            // Show loading state
            const originalHTML = button.innerHTML;
            button.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
            button.disabled = true;
            
            try {
                // Simulate OAuth flow
                await simulateAPICall(1500);
                
                showNotification(`${provider} login coming soon!`, 'info');
                
            } catch (error) {
                showNotification('Social login failed', 'error');
            } finally {
                button.innerHTML = originalHTML;
                button.disabled = false;
            }
        });
    });
}

// =====================================================
// UTILITY FUNCTIONS
// =====================================================

function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function showError(fieldId, message) {
    const input = document.getElementById(fieldId);
    const formGroup = input.closest('.form-group');
    
    // Remove existing error
    const existingError = formGroup.querySelector('.error-message');
    if (existingError) {
        existingError.remove();
    }
    
    // Add error class
    formGroup.classList.add('error');
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${message}`;
    
    const wrapper = input.closest('.password-input-wrapper') || input;
    wrapper.parentNode.insertBefore(errorDiv, wrapper.nextSibling);
    
    // Remove error on input
    input.addEventListener('input', () => {
        formGroup.classList.remove('error');
        errorDiv.remove();
    }, { once: true });
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 2rem;
        right: 2rem;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#06b6d4'};
        color: white;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        z-index: 9999;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        animation: slideIn 0.3s ease-out;
        font-size: 14px;
        font-weight: 500;
    `;
    
    const icon = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-times-circle' : 'fa-info-circle';
    notification.innerHTML = `<i class="fas ${icon}"></i> ${message}`;
    
    document.body.appendChild(notification);
    
    // Add animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(400px);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
    `;
    document.head.appendChild(style);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.animation = 'slideIn 0.3s ease-out reverse';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

function simulateAPICall(delay) {
    return new Promise((resolve) => {
        setTimeout(resolve, delay);
    });
}

// =====================================================
// INPUT ANIMATIONS
// =====================================================

// Add focus effects
document.querySelectorAll('.form-input').forEach(input => {
    input.addEventListener('focus', () => {
        input.parentElement.style.transform = 'scale(1.01)';
    });
    
    input.addEventListener('blur', () => {
        input.parentElement.style.transform = 'scale(1)';
    });
});
