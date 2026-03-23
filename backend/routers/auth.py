"""
routers/auth.py — HanziFlow Auth (Finalna sinhronizovana verzija)
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from jose import jwt
import hashlib, secrets

from core.db import get_db, settings

router = APIRouter()
security = HTTPBearer()

# --- POMOĆNE FUNKCIJE ---

def hash_pw(pw: str, salt: str = "") -> str:
    if not salt: salt = secrets.token_hex(16)
    digest = hashlib.sha256((salt + pw).encode()).hexdigest()
    return f"{salt}${digest}"

def verify_pw(pw: str, stored: str) -> bool:
    if not stored or "$" not in stored:
        return False
    salt, _ = stored.split("$", 1)
    return hash_pw(pw, salt) == stored

def make_token(user_id: str) -> str:
    if not settings.jwt_secret:
        raise ValueError("JWT_SECRET nije konfigurisan!")
    # Koristimo timezone-aware datetime za exp
    payload = {
        "sub": str(user_id), 
        "exp": datetime.now(timezone.utc) + timedelta(days=30)
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
        return payload["sub"]
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

# --- MODELI PODATAKA ---

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str

# --- ENDPOINTI ---

@router.post("/register")
async def register(req: RegisterRequest):
    try:
        db = get_db()
        
        # 1. Provera da li već postoji korisnik
        existing = db.table("profiles").select("id").or_(f"username.eq.{req.username},email.eq.{req.email}").execute()
        if existing.data:
            raise HTTPException(status_code=400, detail="Username or email already in use")

        # 2. Hešovanje lozinke
        pw_hash = hash_pw(req.password)

        # 3. Priprema podataka - sinhronizovano sa SQL bazom
        user_data = {
            "username": req.username,
            "email": req.email,
            "password_hash": pw_hash,
            "xp": 0,
            "level": 1,
            "streak": 0,
            "completed_days": [],           # JSONB
            "achievements": [],             # JSONB
            "vocab": [],                    # JSONB
            "arena_score": 0,
            "audio_enabled": True,
            "pinyin_enabled": True,
            "mistakes": {"words": [], "sentences": []}, # JSONB
            "preferred_quiz_modes": {"type": 3, "draw": 2, "listen": 2, "meaning": 2} # JSONB
        }

        # 4. Upis u bazu (ID će generisati Supabase automatski zbog gen_random_uuid())
        db.table("profiles").insert(user_data).execute()
        
        return {"message": "Account created successfully", "username": req.username}

    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"BACKEND ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database Error: {str(e)}")

@router.post("/login")
async def login(req: LoginRequest):
    try:
        db = get_db()
        # Tražimo korisnika
        res = db.table("profiles").select("*").eq("username", req.username).execute()
        
        if not res.data:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        user = res.data[0]
        
        # Provera lozinke
        if not verify_pw(req.password, user.get("password_hash", "")):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Generisanje tokena
        token = make_token(user["id"])
        
        return {
            "token": token, 
            "profile": {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"],
                "level": user.get("level", 1),
                "xp": user.get("xp", 0)
            }
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"LOGIN ERROR: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/me")
async def me(auth: HTTPAuthorizationCredentials = Depends(security)):
    """
    Korišćenje HTTPBearer-a automatski vadi 'Bearer <token>' iz zaglavlja
    """
    token = auth.credentials
    uid = decode_token(token)
    db = get_db()
    
    res = db.table("profiles").select("*").eq("id", uid).execute()
    
    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")
        
    return res.data[0]