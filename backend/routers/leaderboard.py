from fastapi import APIRouter
from datetime import date, timedelta
router = APIRouter()

def get_rank(score: int) -> dict:
    RANKS = [{"name":"Word Rookie","min":0,"color":"#CD7F32","icon":"🥉"},
             {"name":"Stroke Student","min":500,"color":"#A8A9AD","icon":"⚔️"},
             {"name":"Hanzi Hunter","min":1500,"color":"#FFD700","icon":"🥇"},
             {"name":"Sentence Master","min":4000,"color":"#50C8FF","icon":"💠"},
             {"name":"Fluency King","min":10000,"color":"#B44FE8","icon":"👑"},
             {"name":"Dragon Scholar","min":25000,"color":"#FF4F4F","icon":"🐉"}]
    return [r for r in RANKS if score >= r["min"]][-1]

@router.get("/global")
async def global_board():
    from core.db import get_db
    res = get_db().table("profiles").select("username,xp,level,streak,arena_score,avatar_url").order("xp", desc=True).limit(50).execute()
    entries = []
    for p in (res.data or []):
        entries.append({**p, "rank": get_rank(p.get("arena_score", 0))})
    return entries

@router.get("/weekly")
async def weekly_board():
    from core.db import get_db
    week_ago = (date.today() - timedelta(days=7)).isoformat()
    res = get_db().table("profiles").select("username,xp,level,streak,arena_score,avatar_url,daily_xp_history").limit(100).execute()
    entries = []
    for p in (res.data or []):
        hist = p.get("daily_xp_history", {})
        weekly_xp = sum(v for k, v in hist.items() if k >= week_ago)
        entries.append({"username": p["username"], "xp": p["xp"], "level": p["level"],
                        "weekly_xp": weekly_xp, "streak": p["streak"],
                        "arena_score": p.get("arena_score", 0),
                        "avatar_url": p.get("avatar_url", ""),
                        "rank": get_rank(p.get("arena_score", 0))})
    entries.sort(key=lambda x: x["weekly_xp"], reverse=True)
    return entries[:50]
