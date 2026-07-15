from datetime import datetime
from backend.schemas.chat import ChatRequest
from backend.utils.response import ResponseBuilder
from backend.config.logger import logger
from backend.repositories.chat_repository import chat_repository
from backend.repositories.session_repository import session_repository

class ChatService:

    async def process_chat(
            self,
            request:ChatRequest
    ):
        logger.info("ChatService started")
        await  session_repository.create_session(
            request.session_id
        )
        await session_repository.update_activity(
            request.session_id
        )
        history = await chat_repository.get_recent_message(
            request.session_id
        )
        logger.info(
            f"Loaded{len(history)} previous messages"
        )
        conversation = []
        for message in history:
            conversation.append(
                {
                    "role":message["role"],
                    "content": message["message"]
                }
            )
        conversation.append(
            {
                "role":"user",
                "content":request.question
            }
        )

        await chat_repository.save_message(
            session_id=request.session_id,
            role="user",
            message=request.question,
            language=request.language,
        )
        answer = f"You asked: {request.question}"
        await chat_repository.save_message(
            session_id=request.session_id,
            role="assistant",
            message=answer,
            language=request.language,
        )
        logger.info("Chat response generated")

        return ResponseBuilder.success(
            message="Chat processed successfully",
            data={
                "answer": answer,
                "language": request.language,
                "timestamp": str(datetime.now())
            }
        )