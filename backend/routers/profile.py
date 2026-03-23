from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
import os, uuid
router = APIRouter()

@router.get("/")
async def get_profile(user_id: str):
    from core.db import get_db
    res = get_db().table("profiles").select("*").eq("id", user_id).single().execute()
    if not res.data: raise HTTPException(404, "Not found")
    return res.data

class ProfileUpdate(BaseModel):
    lang: str = None; daily_goal: int = None; audio_enabled: bool = None
    theme: str = None; show_rank: bool = None; show_nickname: bool = None

@router.patch("/")
async def update_profile(req: ProfileUpdate, user_id: str):
    from core.db import get_db
    updates = {k: v for k, v in req.dict().items() if v is not None}
    get_db().table("profiles").update(updates).eq("id", user_id).execute()
    return {"success": True}

@router.post("/avatar")
async def upload_avatar(file: UploadFile = File(...), user_id: str = None):
    from core.db import get_db
    data = await file.read()
    path = f"avatars/{user_id}/{uuid.uuid4()}.jpg"
    get_db().storage.from_("avatars").upload(path, data, {"content-type": file.content_type})
    url = get_db().storage.from_("avatars").get_public_url(path)
    get_db().table("profiles").update({"avatar_url": url}).eq("id", user_id).execute()
    return {"avatar_url": url}
