# GET /api/session/{id}

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException

from app.database import get_db
from app.models.schemas import SessionResponse

router = APIRouter()


@router.get("/api/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str) -> SessionResponse:
    try:
        object_id = ObjectId(session_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid session id.")

    db = get_db()
    doc = await db.sessions.find_one({"_id": object_id})

    if doc is None:
        raise HTTPException(status_code=404, detail="Session not found.")

    doc["id"] = str(doc.pop("_id"))
    return SessionResponse(**doc)
