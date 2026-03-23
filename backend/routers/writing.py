"""
routers/writing.py — AI writing check (same logic as desktop)
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import unicodedata, re, httpx, json, os
from typing import Optional

router = APIRouter()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "google/gemini-3-flash-preview"

def _norm(t: str) -> str:
    t = t.lower().strip()
    t = "".join(c for c in unicodedata.normalize("NFD", t) if unicodedata.category(c) != "Mn")
    for ch in ".,!?;:'\"()-": t = t.replace(ch, " ")
    return " ".join(t.split())

def _tok(t): return {w for w in _norm(t).split() if w and w not in {"a","an","the","to","of","in","on","at","is","are","i","he","she","we","it","and","or","but"}}
def _jac(a, b):
    sa, sb = _tok(a), _tok(b)
    return len(sa & sb) / len(sa | sb) if (sa | sb) else 1.0

async def _ai_check(chinese: str, user_answer: str, refs: list[str], lang: str) -> dict:
    ref_str = " | ".join(refs[:4])
    prompt = f"""You are a lenient Chinese language teacher checking a student's translation.
Chinese sentence: {chinese}
Reference translations: {ref_str}
Student's answer: {user_answer}

SCORING RULES - be generous with synonyms and paraphrases:
- score 90-100: Perfect or near-perfect match
- score 75-89: Same meaning, different words (like=enjoy=love, chat=talk)
- score 60-74: Mostly correct, minor omissions
- score 40-59: Partially correct
- score 0-39: Wrong meaning

ALWAYS ACCEPT (score >= 75): synonyms, different tenses with same meaning, dropped articles
Respond ONLY with valid JSON, feedback in {"Serbian" if lang == "sr" else "English"}:
{{"correct": true/false, "score": 0-100, "feedback": "one short sentence", "suggestion": ""}}"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
            json={"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.2, "max_tokens": 200},
            timeout=15
        )
        data = r.json()
        text = data["choices"][0]["message"]["content"].strip()
        text = text.replace("```json", "").replace("```", "").strip()
        result = json.loads(text)
        return {
            "correct": bool(result.get("correct", False)),
            "score": int(result.get("score", 0)),
            "feedback": str(result.get("feedback", "")),
            "suggestion": str(result.get("suggestion", "")),
        }

class CheckRequest(BaseModel):
    chinese: str
    answer: str
    reference_answers: list[str]
    lang: str = "en"

class GenerateRequest(BaseModel):
    vocab: list[dict]
    weak_hanzi: list[str] = []
    lang: str = "en"

@router.post("/check")
async def check_answer(req: CheckRequest):
    # Local check first
    un = _norm(req.answer)
    for ref in req.reference_answers:
        if un == _norm(ref):
            return {"correct": True, "score": 100, "feedback": "Perfect! ✓", "suggestion": ""}
    best_jac = max((_jac(un, ref) for ref in req.reference_answers), default=0)
    if best_jac >= 0.95:
        return {"correct": True, "score": int(best_jac*100), "feedback": "Excellent! ✓", "suggestion": ""}

    # AI check
    if OPENROUTER_KEY:
        try:
            result = await _ai_check(req.chinese, req.answer, req.reference_answers, req.lang)
            return result
        except Exception as e:
            pass

    # Fallback local
    if best_jac >= 0.68:
        return {"correct": True, "score": int(best_jac*100), "feedback": "Accepted ✓", "suggestion": ""}
    return {"correct": False, "score": int(best_jac*100), "feedback": "Incorrect", "suggestion": req.reference_answers[0] if req.reference_answers else ""}

@router.post("/generate")
async def generate_sentence(req: GenerateRequest):
    if not OPENROUTER_KEY:
        raise HTTPException(503, "AI not available")
    word_info = []
    for w in req.vocab[:22]:
        tag = "[WEAK]" if w.get("hanzi") in req.weak_hanzi else ""
        word_info.append(f"{tag}{w.get('hanzi')}({w.get('pinyin')})={w.get('meaning_en')}")
    prompt = f"""Create ONE Chinese sentence using these words: {', '.join(word_info)}.
Words marked [WEAK] should be prioritized.
Return ONLY JSON:
{{"chinese":"sentence","pinyin":"pinyin","answer_en":"English","answer_sr":"Serbian","words_used":[{{"hanzi":"","en":"","sr":""}}],"difficulty":"easy/medium/hard"}}"""

    async with httpx.AsyncClient() as client:
        r = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={"Authorization": f"Bearer {OPENROUTER_KEY}", "Content-Type": "application/json"},
            json={"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                  "temperature": 0.6, "max_tokens": 350},
            timeout=20
        )
        text = r.json()["choices"][0]["message"]["content"].strip()
        text = text.replace("```json","").replace("```","").strip()
        data = json.loads(text)

        def _exp(meaning):
            parts = [p.strip() for p in str(meaning).split(";")]
            result = []
            for p in parts:
                result.extend([p, p.lower()])
                if p.lower().startswith("to "): result.extend([p[3:], p[3:].lower()])
            return list(dict.fromkeys(result))

        return {
            "chinese": data.get("chinese","").replace(" ",""),
            "pinyin": data.get("pinyin",""),
            "answers": {
                "en": _exp(data.get("answer_en","")),
                "sr": _exp(data.get("answer_sr",""))
            },
            "difficulty": data.get("difficulty","medium"),
        }
