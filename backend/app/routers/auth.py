
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.db.supabase import get_supabase_client

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    token: str
    restaurant_id: str
    restaurant_name: str

# Hardcoded credentials for Demo
DEMO_USER = "sarang"
DEMO_PASS = "password"
DEMO_RESTAURANT_ID = "4c01898c-e005-4311-a6c7-f42c444022a9"

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest):
    """
    Simple login for demo purposes.
    """
    if credentials.username.lower() == DEMO_USER and credentials.password == DEMO_PASS:
        # In a real app, generate a JWT token here
        return {
            "token": "demo-token-sarang-123", 
            "restaurant_id": DEMO_RESTAURANT_ID,
            "restaurant_name": "Sarang Restaurant"
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/verify/{token}")
async def verify_token(token: str):
    """
    Verify the token.
    """
    if token == "demo-token-sarang-123":
        return {
            "authenticated": True,
            "restaurant_id": DEMO_RESTAURANT_ID,
            "restaurant_name": "Sarang Restaurant"
        }
    return {"authenticated": False}
