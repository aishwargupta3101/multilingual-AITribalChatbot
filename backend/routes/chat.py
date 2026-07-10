from backend.services.chat_service import ChatService
from fastapi import APIRouter,Depends
from backend.api.dependencies import get_chat_service
from backend.schemas.chat import ChatRequest

router= APIRouter(
    prefix="/chat",
    tags=["Chat"]

)
@router.post("/")
async  def chat(
        request: ChatRequest,
        chat_service: ChatService = Depends(get_chat_service)
):
    return await chat_service.process_chat(request)