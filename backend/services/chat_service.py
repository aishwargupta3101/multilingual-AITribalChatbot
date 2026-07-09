from datetime import datetime
from backend.schemas.chat import ChatRequest,ChatResponse

class ChatService:
    @staticmethod
    async def process_chat(request:ChatRequest) ->ChatResponse:
        answer = f"You asked:{request.question}"
        return ChatResponse(
            success=True,
            answer=answer,
            language=request.language,
            timestamp=datetime.now()
        )