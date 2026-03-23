from fastapi import APIRouter, HTTPException, UploadFile, File, Form
import httpx, json, os, base64
router = APIRouter()
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

@router.post("/evaluate")
async def evaluate_speaking(audio: UploadFile = File(...), hanzi: str = Form(...), pinyin: str = Form(...)):
    wav_bytes = await audio.read()
    if len(wav_bytes) < 2000: raise HTTPException(400, "Audio too short")
    if not GEMINI_KEY: raise HTTPException(503, "Gemini key required for speaking evaluation")
    prompt = (f"Strict Chinese pronunciation evaluator. Target: '{hanzi}' (pinyin: {pinyin}). "
              "RULES: score=0 if not Chinese. Only high score (70+) if clearly matches pinyin. "
              "Return ONLY JSON: {\"correct\": bool, \"score\": 0-100, \"feedback\": \"one sentence\", \"heard\": \"what you heard\"}")
    payload = {"contents": [{"parts": [
        {"text": prompt},
        {"inline_data": {"mime_type": "audio/wav", "data": base64.b64encode(wav_bytes).decode()}}
    ]}]}
    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}",
            json=payload, timeout=35)
    text = r.json()["candidates"][0]["content"]["parts"][0]["text"].replace("```json","").replace("```","").strip()
    result = json.loads(text)
    # Anti-hallucination check
    heard = result.get("heard", "").lower().replace(" ", "")
    import unicodedata
    def strip_tones(s): return "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    target_py = strip_tones(pinyin.lower().replace(" ", ""))
    heard_py  = strip_tones(heard)
    hanzi_match = any(ch in result.get("heard","") for ch in hanzi if ch.strip())
    overlap = sum(1 for c in target_py if c in heard_py) / max(len(target_py), 1)
    if not hanzi_match and overlap < 0.3 and result.get("score", 0) > 20:
        result["score"] = 0; result["correct"] = False
        result["feedback"] = "Didn't match target. Try again."
    return result
