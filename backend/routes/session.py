from fastapi import APIRouter
from backend.repositories.session_repository import session_repository

router= APIRouter()

@router.get("/sessions")
async def get_sessions():
    sessions = await session_repository.get_all_session()
    return{
        "success":True,
        "session":sessions
    }
@router.delete("/sessions/{session_id}")
async def delete_session(session_id : str):
    await session_repository.delete_session(session_id)
    return{
        "success":True,
        "message":"Session deleted"
    }
