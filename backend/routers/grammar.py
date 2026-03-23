from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx, json, os
router = APIRouter()
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "google/gemini-3-flash-preview"

class GenerateReq(BaseModel):
    known_words: list[str]; performance: str = ""; lang: str = "en"

@router.post("/generate")
async def generate_sentence(req: GenerateReq):
    if not OPENROUTER_KEY: raise HTTPException(503, "AI not available")
    prompt = (f"Chinese teacher. Student knows: {', '.join(req.known_words[:30])}. {req.performance} "
              "Create ONE simple Chinese sentence. Respond with EXACTLY 5 lines:\n"
              "RECENICA: [hanzi sentence]\nIZMESANO: [same words comma-separated, shuffled]\n"
              "ZNACENJE_SR: [Serbian]\nZNACENJE_EN: [English]\nXP: [10-40]")
    async with httpx.AsyncClient() as c:
        r = await c.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            json={"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.3, "max_tokens": 200}, timeout=20)
    text = r.json()["choices"][0]["message"]["content"]
    result = {}
    import re
    for key, prefix in [("correct","RECENICA"),("scrambled","IZMESANO"),
                         ("meaning_sr","ZNACENJE_SR"),("meaning_en","ZNACENJE_EN"),("xp","XP")]:
        m = re.search(rf'^{prefix}\s*:\s*(.+)$', text, re.MULTILINE|re.IGNORECASE)
        if m:
            v = m.group(1).strip()
            result[key] = int(re.findall(r'\d+', v)[0]) if key == "xp" and re.findall(r'\d+', v) else v
    if "correct" not in result: raise HTTPException(500, "AI parse error")
    result["correct"] = result["correct"].replace(" ", "")
    return result

class AnswerReq(BaseModel):
    user_id: str; correct: bool; xp: int = 0

@router.post("/answer")
async def grammar_answer(req: AnswerReq):
    from core.db import get_db
    from datetime import date
    db = get_db()
    res = db.table("profiles").select("grammar_completed,xp,daily_xp,daily_xp_history,completed_days,daily_goal").eq("id", req.user_id).single().execute()
    if not res.data: raise HTTPException(404, "Not found")
    p = res.data
    today = date.today().isoformat()
    new_daily = p.get("daily_xp", 0) + req.xp
    history = p.get("daily_xp_history", {}); history[today] = new_daily
    completed = p.get("completed_days", [])
    if new_daily >= p.get("daily_goal", 100) and today not in completed:
        completed.append(today)
    db.table("profiles").update({
        "grammar_completed": p.get("grammar_completed", 0) + (1 if req.correct else 0),
        "xp": p.get("xp", 0) + req.xp, "daily_xp": new_daily,
        "daily_xp_history": history, "completed_days": completed
    }).eq("id", req.user_id).execute()
    return {"success": True}
