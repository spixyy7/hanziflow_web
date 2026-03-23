"""
core/db.py — HanziFlow Supabase klijent i konfiguracija
"""
import os
from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings
from supabase import create_client, Client

class Settings(BaseSettings):
    # Definišemo varijable sa default praznim stringovima
    supabase_url: str = ""
    supabase_key: str = ""
    openrouter_api_key: str = ""
    gemini_api_key: str = ""
    jwt_secret: str = "hanziflow-secret-change-me"
    frontend_url: str = "http://localhost:3000"

    # VALIDATORI: Ovo automatski čisti navodnike iz .env ili Railway varijabli
    @field_validator("supabase_url", "supabase_key", "jwt_secret", mode="before")
    @classmethod
    def clean_quotes(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip('"').strip("'").strip()
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignoriše ostale varijable koje nisu u klasi

# Inicijalizacija settings-a
settings = Settings()

# Singleton instanca Supabase klijenta
_sb: Optional[Client] = None

def get_db() -> Client:
    """
    Vraća (ili kreira) singleton Supabase klijent.
    """
    global _sb
    if _sb is None:
        # Provera da li su ključne varijable prisutne nakon čišćenja
        if not settings.supabase_url or not settings.supabase_key:
            raise RuntimeError(
                "\n❌ SUPABASE KONFIGURACIJA NIJE PRONAĐENA!\n"
                "Proveri .env fajl ili Railway Variables tab.\n"
                f"URL detektovan: {'DA' if settings.supabase_url else 'NE'}\n"
                f"KEY detektovan: {'DA' if settings.supabase_key else 'NE'}"
            )
        
        try:
            # Kreiranje klijenta
            _sb = create_client(settings.supabase_url, settings.supabase_key)
        except Exception as e:
            raise RuntimeError(f"❌ Neuspešna konekcija na Supabase: {str(e)}")
            
    return _sb