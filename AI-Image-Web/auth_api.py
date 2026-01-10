"""
Authentication API endpoints for FastAPI
Add these routes to your main api.py
"""
from fastapi import FastAPI, Form, Header, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional
import database

app = FastAPI()

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
