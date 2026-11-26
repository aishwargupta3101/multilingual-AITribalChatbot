from fastapi import APIRouter, Depends, HTTPException, Query
from backend.repositories.chat_repository import chat_repository
from backend.repositories.session_repository import session_repository
from backend.auth.auth_routes import get_current_user

router = APIRouter()


@router.get("/history/recent")
async def get_recent_chats(
    limit: int = Query(10, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    sessions = await chat_repository.get_recent_sessions(current_user["id"], limit=limit)
    return {"success": True, "data": sessions}


@router.get("/history/{session_id}")
async def get_history(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    session = await session_repository.get_session(session_id, current_user["id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    history = await chat_repository.get_chat_history(session_id, current_user["id"])
    return {"success": True, "message": history}
