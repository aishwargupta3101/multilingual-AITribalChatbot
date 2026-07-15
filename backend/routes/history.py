from fastapi import APIRouter

from backend.repositories.chat_repository import chat_repository
router = APIRouter()

@router.get("/history/{session_id}")
async def get_history(session_id:str):
    history = await chat_repository.get_chat_history(
        session_id
    )
    return {
        "success":True,
        "message":history
    }