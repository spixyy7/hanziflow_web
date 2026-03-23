from fastapi import APIRouter
from pydantic import BaseModel
import httpx, json, os
from datetime import date
router = APIRouter()
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "google/gemini-3-flash-preview"

class CoachReq(BaseModel):
    user_id: str; goal: int; history: dict

@router.post("/check")
async def check(req: CoachReq):
    if not OPENROUTER_KEY: return {"action": "keep", "suggested_goal": req.goal, "message": "Keep up the great work!"}
    from core.db import get_db
    db = get_db()
    today = date.today().isoformat()
    res = db.table("profiles").select("last_goal_check,cached_coach_msg").eq("id", req.user_id).single().execute()
    p = res.data or {}
    if p.get("last_goal_check") == today and p.get("cached_coach_msg"):
        return json.loads(p["cached_coach_msg"])
    hist_str = ", ".join(f"{k}: {v}XP" for k, v in sorted(req.history.items())[-7:])
    prompt = (f"AI language coach. Daily goal: {req.goal} XP. History: {hist_str}. "
              "Analyze and suggest. Return ONLY JSON: "
              "{\"action\": \"increase|decrease|keep\", \"suggested_goal\": number, \"message\": \"short encouraging message\"}")
    async with httpx.AsyncClient() as c:
        r = await c.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            json={"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.3, "max_tokens": 150}, timeout=15)
    text = r.json()["choices"][0]["message"]["content"].replace("```json","").replace("```","").strip()
    result = json.loads(text)
    db.table("profiles").update({"last_goal_check": today, "cached_coach_msg": json.dumps(result)}).eq("id", req.user_id).execute()
    return result
