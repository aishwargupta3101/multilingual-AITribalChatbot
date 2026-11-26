from fastapi import APIRouter, Depends, HTTPException
from backend.repositories.session_repository import session_repository
from backend.auth.auth_routes import get_current_user

router = APIRouter()


@router.get("/sessions")
async def get_sessions(current_user: dict = Depends(get_current_user)):
    sessions = await session_repository.get_all_session(current_user["id"])
    return {"success": True, "session": sessions}


@router.delete("/sessions/{session_id}")
async def delete_session(
    session_id: str,
    current_user: dict = Depends(get_current_user),
):
    deleted = await session_repository.delete_session(session_id, current_user["id"])
    if not deleted:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"success": True, "message": "Session deleted"}
