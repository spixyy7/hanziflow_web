from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import random, httpx, json, os, re
router = APIRouter()
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "google/gemini-3-flash-preview"

@router.get("/words")
async def get_arena_words(user_id: str):
    from core.db import get_db
    res = get_db().table("profiles").select("vocab").eq("id", user_id).single().execute()
    vocab = res.data.get("vocab", []) if res.data else []
    if len(vocab) < 4: raise HTTPException(400, "Need at least 4 words for Arena")
    sample = random.sample(vocab, min(30, len(vocab)))
    return sample

class ScoreReq(BaseModel):
    user_id: str; score: int; combo: int; correct: int; total: int

@router.post("/score")
async def submit_score(req: ScoreReq):
    from core.db import get_db
    from datetime import date
    db = get_db()
    res = db.table("profiles").select("arena_score,xp,daily_xp,daily_xp_history,completed_days,daily_goal,streak_earned_today,streak,longest_streak").eq("id", req.user_id).single().execute()
    if not res.data: raise HTTPException(404, "Not found")
    p = res.data
    xp_gain = req.score // 10 + req.combo * 5
    today = date.today().isoformat()
    new_daily = p.get("daily_xp", 0) + xp_gain
    history = p.get("daily_xp_history", {}); history[today] = new_daily
    completed = p.get("completed_days", [])
    if new_daily >= p.get("daily_goal", 100) and today not in completed:
        completed.append(today)
    # Streak
    streak = p.get("streak", 0)
    if p.get("streak_earned_today") != today:
        streak += 1
    db.table("profiles").update({
        "arena_score": max(p.get("arena_score", 0), req.score),
        "xp": p.get("xp", 0) + xp_gain,
        "daily_xp": new_daily, "daily_xp_history": history,
        "completed_days": completed, "streak": streak,
        "longest_streak": max(p.get("longest_streak", 0), streak),
        "streak_earned_today": today,
    }).eq("id", req.user_id).execute()
    return {"xp_gained": xp_gain}

class CommentReq(BaseModel):
    score: int; combo: int; correct: int; total: int; time_left: int; lang: str = "en"

@router.post("/comment")
async def get_comment(req: CommentReq):
    if not OPENROUTER_KEY: return {"comment": "Great job!"}
    acc = round((req.correct / max(req.total, 1)) * 100 / 20) * 20
    lang_i = "in Serbian, max 12 words" if req.lang == "sr" else "in English, max 12 words"
    prompt = (f"Exciting sports commentator for Chinese word game. "
              f"Score={req.score}, combo={req.combo}, accuracy={acc}%, time={req.time_left}s. "
              f"ONE short exciting comment {lang_i}. No emojis.")
    async with httpx.AsyncClient() as c:
        r = await c.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            json={"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.9, "max_tokens": 60}, timeout=8)
    return {"comment": r.json()["choices"][0]["message"]["content"].strip()}
