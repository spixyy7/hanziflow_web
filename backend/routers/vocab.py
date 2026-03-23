from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import httpx, json, os, base64
router = APIRouter()
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "google/gemini-3-flash-preview"

class WordIn(BaseModel):
    hanzi: str; pinyin: str; meaning_sr: str = ""; meaning_en: str = ""; xp: int = 15

@router.get("/")
async def list_vocab(user_id: str):
    from core.db import get_db
    res = get_db().table("profiles").select("vocab").eq("id", user_id).single().execute()
    return res.data.get("vocab", []) if res.data else []

@router.post("/")
async def add_word(req: WordIn, user_id: str):
    from core.db import get_db
    db = get_db()
    res = db.table("profiles").select("vocab").eq("id", user_id).single().execute()
    vocab = res.data.get("vocab", []) if res.data else []
    if any(w.get("hanzi") == req.hanzi for w in vocab):
        raise HTTPException(400, "Word already in vocabulary")
    # AI translate if missing
    if (not req.meaning_sr or not req.meaning_en) and OPENROUTER_KEY:
        meaning = req.meaning_sr or req.meaning_en
        prompt = f"Translate this word meaning: '{meaning}'. Return ONLY JSON: {{\"meaning_sr\": \"Serbian\", \"meaning_en\": \"English\"}}"
        async with httpx.AsyncClient() as c:
            r = await c.post("https://openrouter.ai/api/v1/chat/completions",
                headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
                json={"model": MODEL, "messages": [{"role": "user", "content": prompt}], "max_tokens": 80},
                timeout=10)
            try:
                data = json.loads(r.json()["choices"][0]["message"]["content"].replace("```json","").replace("```","").strip())
                req.meaning_sr = data.get("meaning_sr", req.meaning_sr)
                req.meaning_en = data.get("meaning_en", req.meaning_en)
            except: pass
    from datetime import date
    word = {**req.dict(), "interval": 0, "step": 0, "ease": 2.5,
            "next_review": date.today().isoformat(), "total_seen": 0,
            "total_correct": 0, "consecutive_wrong": 0, "avg_response_time": 0.0}
    vocab.append(word)
    db.table("profiles").update({"vocab": vocab}).eq("id", user_id).execute()
    return word

@router.delete("/{hanzi}")
async def delete_word(hanzi: str, user_id: str):
    from core.db import get_db
    db = get_db()
    res = db.table("profiles").select("vocab").eq("id", user_id).single().execute()
    vocab = [w for w in (res.data.get("vocab", []) if res.data else []) if w.get("hanzi") != hanzi]
    db.table("profiles").update({"vocab": vocab}).eq("id", user_id).execute()
    return {"success": True}

@router.post("/extract")
async def extract_from_file(file: UploadFile = File(...), user_id: str = None):
    if not OPENROUTER_KEY: raise HTTPException(503, "AI not available")
    content = await file.read()
    ext = file.filename.lower().split(".")[-1] if file.filename else ""
    text = ""; image_b64 = None
    if ext in ("png", "jpg", "jpeg"):
        image_b64 = base64.b64encode(content).decode()
    elif ext == "txt":
        text = content.decode("utf-8", errors="ignore")
    prompt = "Extract all Chinese words from this content. Return ONLY a JSON array: [{\"hanzi\":\"字\",\"pinyin\":\"zì\",\"meaning_en\":\"character\",\"meaning_sr\":\"karakter\",\"xp\":15}]"
    messages = [{"role": "user", "content": [{"type": "text", "text": prompt}]}]
    if image_b64:
        messages[0]["content"].append({"type": "image_url", "image_url": {"url": f"data:{file.content_type};base64,{image_b64}"}})
    elif text:
        messages[0]["content"].append({"type": "text", "text": text})
    async with httpx.AsyncClient() as c:
        r = await c.post("https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}"},
            json={"model": MODEL, "messages": messages, "max_tokens": 1000}, timeout=30)
        raw = r.json()["choices"][0]["message"]["content"].replace("```json","").replace("```","").strip()
        words = json.loads(raw)
    return {"words": words}
