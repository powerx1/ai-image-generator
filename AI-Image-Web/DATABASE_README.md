# Database Setup Guide

## Overview

This project uses SQLite for user authentication and session management. The database is automatically created when you first run the application.

## Files

- **schema.sql** - Database schema with tables for users, sessions, and generated images
- **database.py** - Python module with database operations
- **auth_api.py** - FastAPI authentication endpoints
- **users.db** - SQLite database file (auto-created, gitignored)

## Database Schema

### Tables

#### `users`
- `id` - Primary key
- `username` - Unique username
- `email` - Unique email address
- `password_hash` - Hashed password
- `full_name` - User's full name
- `created_at` - Registration timestamp
- `last_login` - Last login timestamp
- `is_active` - Account status
- `is_verified` - Email verification status

#### `sessions`
- `id` - Primary key
- `user_id` - Foreign key to users
- `session_token` - Unique session identifier
- `expires_at` - Session expiration time (7 days)
- `ip_address` - Client IP
- `user_agent` - Client browser info

#### `generated_images`
- `id` - Primary key
- `user_id` - Foreign key to users
- `image_path` - Path to generated image
- `prompt` - Generation prompt
- `mode` - txt2img or img2img
- `parameters` - JSON with generation settings
- `created_at` - Generation timestamp

## Quick Start

### 1. Initialize Database

The database is automatically initialized when you import the `database` module:

```python
import database
```

Or manually:

```python
from database import init_database
init_database()
```

### 2. Add Auth Routes to Your API

**Option A: Include in existing api.py**

```python
from fastapi import FastAPI, Form, Header
from typing import Optional
import database

# Add these endpoints to your existing api.py

@app.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    full_name: Optional[str] = Form(None)
):
    success, message = database.register_user(username, email, password, full_name)
    return {"success": success, "message": message}

@app.post("/login")
async def login(username: str = Form(...), password: str = Form(...)):
    success, message, user_data = database.login_user(username, password)
    return {"success": success, "message": message, "user": user_data}
```

**Option B: Use separate auth_api.py**

Merge the routes from `auth_api.py` into your main `api.py`.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/register` | POST | Register new user |
| `/login` | POST | Login and get session token |
| `/logout` | POST | Logout (invalidate session) |
| `/verify` | GET | Verify session token |
| `/my-images` | GET | Get user's generated images |

## Usage Examples

### Register a User

```bash
curl -X POST "http://localhost:8000/register" \
  -F "username=john" \
  -F "email=john@example.com" \
  -F "password=mypassword" \
  -F "full_name=John Doe"
```

### Login

```bash
curl -X POST "http://localhost:8000/login" \
  -F "username=john" \
  -F "password=mypassword"
```

Response:
```json
{
  "success": true,
  "message": "Login successful",
  "user": {
    "id": 1,
    "username": "john",
    "email": "john@example.com",
    "session_token": "abc123..."
  }
}
```

### Verify Session

```bash
curl -X GET "http://localhost:8000/verify" \
  -H "Authorization: Bearer YOUR_SESSION_TOKEN"
```

## Frontend Integration

Store the session token in localStorage:

```javascript
// After login
const response = await fetch('/login', {
    method: 'POST',
    body: formData
});
const data = await response.json();
if (data.success) {
    localStorage.setItem('session_token', data.user.session_token);
}

// For authenticated requests
fetch('/generate', {
    method: 'POST',
    headers: {
        'Authorization': `Bearer ${localStorage.getItem('session_token')}`
    },
    body: formData
});
```

## Security Notes

⚠️ **Important for Production:**

1. **Change Default Admin Password** - The schema includes a default admin user (password: `admin123`)
2. **Use HTTPS** - Always use HTTPS in production
3. **Upgrade Hashing** - Consider using bcrypt instead of SHA-256
4. **Add Rate Limiting** - Prevent brute force attacks
5. **Email Verification** - Implement email verification for new users
6. **CSRF Protection** - Add CSRF tokens for form submissions

## Upgrading to bcrypt

For better security, upgrade password hashing:

```bash
pip install bcrypt
```

Update in `database.py`:

```python
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
```

## Troubleshooting

**Database locked error:**
- Only one process can write at a time
- Consider PostgreSQL/MySQL for production

**Permission denied:**
- Check file permissions on `users.db`
- Ensure write access to the directory

**Module not found:**
- Make sure all files are in the same directory
- Check `sys.path` includes the correct directory
