"""
backend/main.py — HanziFlow FastAPI Glavni Ulaz
"""
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Uvoz podešavanja i ruter-a
from core.db import settings
from routers import (
    auth, profile, vocab, quiz, writing, 
    grammar, speaking, arena, audio, 
    leaderboard, coach, mistakes
)

# Inicijalizacija aplikacije
app = FastAPI(
    title="HanziFlow API", 
    version="1.0.0",
    description="Backend za HanziFlow aplikaciju za učenje kineskog jezika"
)

# --- CORS PODEŠAVANJA ---
# Definišemo listu dozvoljenih izvora (frontenda)
origins = [
    "http://localhost:3000",           # Lokalni Next.js/React
    "http://127.0.0.1:3000",          # Alternativni lokalni IP
    "https://hanziflowwebb.vercel.app" # Produkcioni Vercel URL
]

# Ako postoji FRONTEND_URL u .env (iz core.db settings), dodajemo ga u listu
if settings.frontend_url and settings.frontend_url not in origins:
    origins.append(settings.frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],               # Dozvoljava GET, POST, PUT, DELETE, itd.
    allow_headers=["*"],               # Dozvoljava Authorization i Content-Type heder-e
)

# --- RUTERS (Registracija svih modula) ---
app.include_router(auth.router,        prefix="/auth",        tags=["Autentifikacija"])
app.include_router(profile.router,     prefix="/profile",     tags=["Profil"])
app.include_router(vocab.router,       prefix="/vocab",       tags=["Rečnik"])
app.include_router(quiz.router,        prefix="/quiz",        tags=["Kvizovi"])
app.include_router(writing.router,     prefix="/writing",     tags=["Pisanje"])
app.include_router(grammar.router,     prefix="/grammar",     tags=["Gramatika"])
app.include_router(speaking.router,    prefix="/speaking",    tags=["Govor"])
app.include_router(arena.router,       prefix="/arena",       tags=["Arena"])
app.include_router(audio.router,       prefix="/audio",       tags=["Audio"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["Leaderboard"])
app.include_router(coach.router,       prefix="/coach",       tags=["AI Coach"])
app.include_router(mistakes.router,    prefix="/mistakes",    tags=["Greške"])

# --- OSNOVNI ENDPOINTI ---

@app.get("/")
async def root():
    return {
        "app": "HanziFlow API",
        "status": "online",
        "docs": "/docs"  # Putanja do automatske Swagger dokumentacije
    }

@app.get("/health")
def health(): 
    return {
        "status": "ok", 
        "version": "1.0.0", 
        "database": "connected" # get_db() bi se ovde moglo pozvati za proveru
    }

# Ako imaš folder za statičke fajlove (npr. slike karaktera ili audio snimke)
# if os.path.exists("static"):
#     app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    # Pokretanje za lokalni test (na Railway-u uvicorn ide kroz start komandu)
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)