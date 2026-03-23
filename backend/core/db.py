"""
core/db.py — Supabase client + settings
"""
from supabase import create_client, Client
from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    supabase_url: str = ""
    supabase_key: str = ""
    openrouter_api_key: str = ""
    gemini_api_key: str = ""
    jwt_secret: str = "hanziflow-secret-change-me"
    frontend_url: str = "http://localhost:3000"  # ← dodato

    class Config:
        env_file = ".env"
        extra = "ignore"  # ← ignoriši nepoznate env varijable

settings = Settings()

_sb: Client = None

def get_db() -> Client:
    global _sb
    if _sb is None:
        if not settings.supabase_url or not settings.supabase_key:
            raise RuntimeError(
                "Supabase nije konfigurisan!\n"
                "Otvori backend/.env i popuni:\n"
                "  SUPABASE_URL=https://xxx.supabase.co\n"
                "  SUPABASE_KEY=tvoj_service_role_key"
            )
        _sb = create_client(settings.supabase_url, settings.supabase_key)
    return _sb