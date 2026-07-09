from backend.services.chat_service import ChatService
from fastapi import APIRouter
from backend.schemas.chat import ChatRequest,ChatResponse

router= APIRouter(
    prefix="/chat",
    tags=["Chat"]

)
@router.post(
    "/",
    response_model=ChatResponse
)
async  def chat(request: ChatRequest):
    return await ChatService.process_chat(request)