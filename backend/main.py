"""
backend/main.py — HanziFlow FastAPI backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routers import auth, profile, vocab, quiz, writing, grammar, speaking, arena, audio, leaderboard, coach, mistakes

app = FastAPI(title="HanziFlow API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers
app.include_router(auth.router,        prefix="/auth",        tags=["auth"])
app.include_router(profile.router,     prefix="/profile",     tags=["profile"])
app.include_router(vocab.router,       prefix="/vocab",       tags=["vocab"])
app.include_router(quiz.router,        prefix="/quiz",        tags=["quiz"])
app.include_router(writing.router,     prefix="/writing",     tags=["writing"])
app.include_router(grammar.router,     prefix="/grammar",     tags=["grammar"])
app.include_router(speaking.router,    prefix="/speaking",    tags=["speaking"])
app.include_router(arena.router,       prefix="/arena",       tags=["arena"])
app.include_router(audio.router,       prefix="/audio",       tags=["audio"])
app.include_router(leaderboard.router, prefix="/leaderboard", tags=["leaderboard"])
app.include_router(coach.router,       prefix="/coach",       tags=["coach"])
app.include_router(mistakes.router,    prefix="/mistakes",    tags=["mistakes"])

@app.get("/health")
def health(): return {"status": "ok", "version": "1.0.0"}
