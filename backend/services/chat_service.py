from datetime import datetime
from backend.schemas.chat import ChatRequest
from backend.utils.response import ResponseBuilder
from backend.config.logger import logger

class ChatService:

    async def process_chat(
            self,
            request:ChatRequest
    ):
        logger.info("ChatService started")
        answer = f"You asked: {request.question}"
        logger.info("Chat response generated")

        return ResponseBuilder.success(
            message="Chat processed successfully",
            data={
                "answer": answer,
                "language": request.language,
                "timestamp": str(datetime.now())
            }
        )