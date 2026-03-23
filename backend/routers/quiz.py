"""
routers/quiz.py — Quiz endpoints with SM2 adaptive learning
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import date, timedelta
import random, httpx, json, os

router = APIRouter()
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "google/gemini-3-flash-preview"

def sm2_update(word: dict, quality: int, response_time: float = 5.0) -> dict:
    w = dict(word)
    w["total_seen"] = w.get("total_seen", 0) + 1
    alpha = 0.3
    w["avg_response_time"] = (
        alpha * response_time + (1 - alpha) * w.get("avg_response_time", 0)
        if w.get("avg_response_time", 0) > 0 else response_time
    )
    if quality >= 3:
        w["total_correct"] = w.get("total_correct", 0) + 1
        w["consecutive_wrong"] = 0
    else:
        w["consecutive_wrong"] = w.get("consecutive_wrong", 0) + 1
    ease = max(1.3, w.get("ease", 2.5) + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    w["ease"] = ease
    step = w.get("step", 0)
    interval = w.get("interval", 0)
    if quality < 3:
        step = 0; interval = 0
    elif step == 0:
        interval = 1; step = 1
    elif step == 1:
        interval = 6; step = 2
    else:
        interval = max(1, round(interval * ease))
    w["step"] = step
    w["interval"] = interval
    w["next_review"] = (date.today() + timedelta(days=interval)).isoformat()
    return w

def compute_weight(word: dict) -> float:
    today = date.today().isoformat()
    days_overdue = max(0, (date.today() - date.fromisoformat(
        word.get("next_review", today))).days)
    acc = word.get("total_correct", 0) / max(word.get("total_seen", 1), 1)
    return max(0.1, (1 - acc) * 3 + days_overdue * 0.5 + word.get("consecutive_wrong", 0) * 2)

@router.get("/words")
async def get_quiz_words(user_id: str, count: int = 10):
    from core.db import get_db
    db = get_db()
    res = db.table("profiles").select("vocab").eq("id", user_id).single().execute()
    if not res.data: raise HTTPException(404, "User not found")
    vocab = res.data.get("vocab", [])
    if not vocab: raise HTTPException(400, "No vocabulary yet")
    today = date.today().isoformat()
    due = [w for w in vocab if w.get("next_review", today) <= today]
    if len(due) < count:
        rest = [w for w in vocab if w not in due]
        random.shuffle(rest)
        due += rest[:count - len(due)]
    due.sort(key=compute_weight, reverse=True)
    return due[:count]

class AnswerReq(BaseModel):
    user_id: str; hanzi: str; quality: int; response_time: float; xp_gained: int = 0

@router.post("/answer")
async def submit_answer(req: AnswerReq):
    from core.db import get_db
    db = get_db()
    res = db.table("profiles").select("*").eq("id", req.user_id).single().execute()
    if not res.data: raise HTTPException(404, "User not found")
    profile = res.data
    vocab = [sm2_update(w, req.quality, req.response_time) if w.get("hanzi") == req.hanzi else w
             for w in profile.get("vocab", [])]
    today = date.today().isoformat()
    new_daily = profile.get("daily_xp", 0) + req.xp_gained
    history = profile.get("daily_xp_history", {}); history[today] = new_daily
    completed = profile.get("completed_days", [])
    if new_daily >= profile.get("daily_goal", 100) and today not in completed:
        completed.append(today)
    updates = {"vocab": vocab, "daily_xp": new_daily, "daily_xp_history": history,
               "completed_days": completed, "xp": profile.get("xp", 0) + req.xp_gained,
               "total_answered": profile.get("total_answered", 0) + 1}
    if req.quality >= 3:
        updates["total_correct"] = profile.get("total_correct", 0) + 1
    db.table("profiles").update(updates).eq("id", req.user_id).execute()
    return {"success": True, "correct": req.quality >= 3}

class FeedbackReq(BaseModel):
    stats_summary: str; weak_words: list[str]; lang: str = "en"

@router.post("/feedback")
async def session_feedback(req: FeedbackReq):
    if not OPENROUTER_KEY: return {"feedback": "Great session! Keep practicing."}
    lang_i = "in Serbian" if req.lang == "sr" else "in English"
    prompt = (f"Chinese tutor. Session: {req.stats_summary}. Weak words: {', '.join(req.weak_words[:5])}. "
              f"Give 2-3 sentences of encouraging feedback {lang_i}.")
    async with httpx.AsyncClient() as c:
        r = await c.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            json={"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.7, "max_tokens": 150}, timeout=15)
    return {"feedback": r.json()["choices"][0]["message"]["content"].strip()}
