"""
Database module for user authentication and session management
Uses SQLite for simplicity and portability
"""
import sqlite3
import hashlib
import secrets
import os
from datetime import datetime, timedelta
from typing import Optional, Tuple
import json

DATABASE_PATH = os.path.join(os.path.dirname(__file__), "users.db")


def get_db_connection():
    """Create and return a database connection"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn


def init_database():
    """Initialize the database with schema"""
    conn = get_db_connection()
    
    # Read and execute schema
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")


def hash_password(password: str) -> str:
    """Hash a password using SHA-256"""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a password against its hash"""
    return hash_password(password) == password_hash


def generate_session_token() -> str:
    """Generate a secure random session token"""
    return secrets.token_urlsafe(32)


def register_user(username: str, email: str, password: str, full_name: str = None) -> Tuple[bool, str]:
    """
    Register a new user
    Returns: (success: bool, message: str)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if username or email already exists
        cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", (username, email))
        if cursor.fetchone():
            return False, "Username or email already exists"
        
        # Hash password and insert user
        password_hash = hash_password(password)
        cursor.execute(
            """INSERT INTO users (username, email, password_hash, full_name) 
               VALUES (?, ?, ?, ?)""",
            (username, email, password_hash, full_name)
        )
        
        conn.commit()
        conn.close()
        return True, "Registration successful"
    
    except sqlite3.IntegrityError:
        return False, "Username or email already exists"
    except Exception as e:
        return False, f"Registration failed: {str(e)}"


def login_user(username_or_email: str, password: str, ip_address: str = None, user_agent: str = None) -> Tuple[bool, str, Optional[dict]]:
    """
    Login a user and create a session
    Returns: (success: bool, message: str, user_data: dict or None)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Find user by username or email
        cursor.execute(
            """SELECT id, username, email, password_hash, full_name, is_active 
               FROM users WHERE (username = ? OR email = ?) AND is_active = 1""",
            (username_or_email, username_or_email)
        )
        user = cursor.fetchone()
        
        if not user:
            return False, "Invalid username/email or password", None
        
        # Verify password
        if not verify_password(password, user['password_hash']):
            return False, "Invalid username/email or password", None
        
        # Create session token
        session_token = generate_session_token()
        expires_at = datetime.now() + timedelta(days=7)  # Session valid for 7 days
        
        cursor.execute(
            """INSERT INTO sessions (user_id, session_token, expires_at, ip_address, user_agent)
               VALUES (?, ?, ?, ?, ?)""",
            (user['id'], session_token, expires_at, ip_address, user_agent)
        )
        
        # Update last login
        cursor.execute(
            "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
            (user['id'],)
        )
        
        conn.commit()
        conn.close()
        
        # Return user data
        user_data = {
            'id': user['id'],
            'username': user['username'],
            'email': user['email'],
            'full_name': user['full_name'],
            'session_token': session_token
        }
        
        return True, "Login successful", user_data
    
    except Exception as e:
        return False, f"Login failed: {str(e)}", None


def verify_session(session_token: str) -> Tuple[bool, Optional[dict]]:
    """
    Verify if a session token is valid
    Returns: (valid: bool, user_data: dict or None)
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT s.user_id, s.expires_at, u.username, u.email, u.full_name
               FROM sessions s
               JOIN users u ON s.user_id = u.id
               WHERE s.session_token = ? AND s.expires_at > CURRENT_TIMESTAMP""",
            (session_token,)
        )
        session = cursor.fetchone()
        conn.close()
        
        if not session:
            return False, None
        
        user_data = {
            'id': session['user_id'],
            'username': session['username'],
            'email': session['email'],
            'full_name': session['full_name']
        }
        
        return True, user_data
    
    except Exception as e:
        print(f"Session verification failed: {e}")
        return False, None


def logout_user(session_token: str) -> bool:
    """
    Logout a user by deleting their session
    Returns: success: bool
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM sessions WHERE session_token = ?", (session_token,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Logout failed: {e}")
        return False


def save_generated_image(user_id: int, image_path: str, prompt: str, negative_prompt: str = "", 
                        mode: str = "txt2img", parameters: dict = None):
    """Save a record of a generated image"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        params_json = json.dumps(parameters) if parameters else None
        
        cursor.execute(
            """INSERT INTO generated_images (user_id, image_path, prompt, negative_prompt, mode, parameters)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (user_id, image_path, prompt, negative_prompt, mode, params_json)
        )
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Failed to save image record: {e}")
        return False


def get_user_images(user_id: int, limit: int = 50):
    """Get a user's generated images"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT id, image_path, prompt, mode, created_at
               FROM generated_images
               WHERE user_id = ?
               ORDER BY created_at DESC
               LIMIT ?""",
            (user_id, limit)
        )
        
        images = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return images
    except Exception as e:
        print(f"Failed to fetch user images: {e}")
        return []


# Initialize database on module import
if not os.path.exists(DATABASE_PATH):
    init_database()
