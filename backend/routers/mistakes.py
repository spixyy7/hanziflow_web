from fastapi import APIRouter, HTTPException
router = APIRouter()

@router.get("/")
async def list_mistakes(user_id: str):
    from core.db import get_db
    res = get_db().table("profiles").select("mistakes").eq("id", user_id).single().execute()
    return res.data.get("mistakes", {"words": [], "sentences": []}) if res.data else {"words": [], "sentences": []}

@router.delete("/{mistake_type}/{identifier}")
async def resolve_mistake(mistake_type: str, identifier: str, user_id: str):
    from core.db import get_db
    db = get_db()
    res = db.table("profiles").select("mistakes").eq("id", user_id).single().execute()
    if not res.data: raise HTTPException(404, "Not found")
    mistakes = res.data.get("mistakes", {"words": [], "sentences": []})
    if mistake_type == "word":
        mistakes["words"] = [m for m in mistakes["words"] if m.get("hanzi") != identifier]
    elif mistake_type == "sentence":
        mistakes["sentences"] = [m for m in mistakes["sentences"] if m.get("correct") != identifier]
    db.table("profiles").update({"mistakes": mistakes}).eq("id", user_id).execute()
    return {"success": True}
