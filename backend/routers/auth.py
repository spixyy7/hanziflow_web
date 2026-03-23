"""
routers/auth.py
"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from jose import jwt
import hashlib, secrets

from core.db import get_db, settings

router = APIRouter()

def hash_pw(pw: str, salt: str = "") -> str:
    if not salt: salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + pw).encode()).hexdigest()
    return f"{salt}${digest}"

def verify_pw(pw: str, stored: str) -> bool:
    if "$" in stored:
        salt, _ = stored.split("$", 1)
        return hash_pw(pw, salt) == stored
    return hashlib.sha256(pw.encode()).hexdigest() == stored

def make_token(user_id: str) -> str:
    payload = {"sub": user_id, "exp": datetime.utcnow() + timedelta(days=30)}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str) -> str:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])["sub"]
    except Exception:
        raise HTTPException(401, "Invalid token")

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

@router.post("/login")
async def login(req: LoginRequest):
    db = get_db()
    res = db.table("profiles").select("*").eq("username", req.username).single().execute()
    if not res.data:
        raise HTTPException(401, "Invalid username or password")
    user = res.data
    if not verify_pw(req.password, user["password_hash"]):
        raise HTTPException(401, "Invalid username or password")
    token = make_token(user["id"])
    return {"token": token, "profile": user}

@router.post("/register")
async def register(req: RegisterRequest):
    db = get_db()
    # Check exists
    existing = db.table("profiles").select("id").eq("username", req.username).execute()
    if existing.data:
        raise HTTPException(400, "Username already taken")
    pw_hash = hash_pw(req.password)
    user = {
        "username": req.username,
        "email": req.email,
        "password_hash": pw_hash,
        "xp": 0, "level": 1, "streak": 0, "daily_xp": 0,
        "daily_goal": 100, "lang": "en", "vocab": [], "achievements": [],
        "mistakes": {"words": [], "sentences": []},
        "daily_xp_history": {}, "completed_days": [],
        "preferred_quiz_modes": {"type": 3, "draw": 2, "listen": 2, "meaning": 2},
        "audio_enabled": True, "theme": "system", "streak_shields": 2,
        "arena_score": 0, "total_correct": 0, "total_answered": 0,
        "grammar_completed": 0, "longest_streak": 0,
    }
    res = db.table("profiles").insert(user).execute()
    return {"message": "Account created", "username": req.username}

@router.get("/me")
async def me(token: str = Depends(lambda r: r.headers.get("Authorization", "").replace("Bearer ", ""))):
    uid = decode_token(token)
    db = get_db()
    res = db.table("profiles").select("*").eq("id", uid).single().execute()
    if not res.data: raise HTTPException(404, "User not found")
    return res.data
