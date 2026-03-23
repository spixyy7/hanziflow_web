"""
routers/audio.py — TTS endpoint
"""
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io, os

router = APIRouter()

GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

@router.get("/tts")
async def tts(text: str, lang: str = "zh"):
    """Returns audio/mpeg stream for given text."""
    # Try gTTS (free, no key needed)
    try:
        from gtts import gTTS
        tts_lang = "zh" if lang == "zh" else "en"
        tts_obj = gTTS(text=text, lang=tts_lang, slow=False)
        buf = io.BytesIO()
        tts_obj.write_to_fp(buf)
        buf.seek(0)
        return StreamingResponse(buf, media_type="audio/mpeg",
                                 headers={"Cache-Control": "public, max-age=86400"})
    except Exception:
        pass

    # Fallback: Gemini TTS
    if GEMINI_KEY:
        try:
            import httpx, base64, wave
            voice = "Kore" if lang == "zh" else "Aoede"
            payload = {
                "contents": [{"parts": [{"text": text}]}],
                "generationConfig": {
                    "responseModalities": ["AUDIO"],
                    "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}
                }
            }
            async with httpx.AsyncClient() as client:
                r = await client.post(
                    f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-tts:generateContent?key={GEMINI_KEY}",
                    json=payload, timeout=15)
                resp = r.json()
                parts = resp["candidates"][0]["content"]["parts"]
                for part in parts:
                    key = "inlineData" if "inlineData" in part else "inline_data" if "inline_data" in part else None
                    if key:
                        pcm = base64.b64decode(part[key]["data"])
                        buf = io.BytesIO()
                        with wave.open(buf, "wb") as wf:
                            wf.setnchannels(1); wf.setsampwidth(2); wf.setframerate(24000)
                            wf.writeframes(pcm)
                        buf.seek(0)
                        return StreamingResponse(buf, media_type="audio/wav")
        except Exception:
            pass

    return StreamingResponse(io.BytesIO(), media_type="audio/mpeg")
