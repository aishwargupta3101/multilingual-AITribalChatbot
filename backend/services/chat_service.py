from datetime import datetime
from backend.schemas.chat import ChatRequest
from backend.utils.response import ResponseBuilder
from backend.config.logger import logger
from backend.repositories.chat_repository import chat_repository
from backend.repositories.session_repository import session_repository
from backend.llm.llama_service import llama_service
import time

class ChatService:

    async def process_chat(
            self,
            request:ChatRequest
    ):
        logger.info(
            f"Session : {request.session_id}"
        )
        logger.info(
            f"Question :{request.question}"
        )
        question = request.question[:2000]
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
                "content":(
                    f"Please answer in {request.language}.\n\n"
                    f"{request.question}"
                )
            }
        )

        await chat_repository.save_message(
            session_id=request.session_id,
            role="user",
            message=question,
            language=request.language,
        )
        start = time.time()
        answer =  await llama_service.generate_response(
            conversation
        )
        end= time.time()
        logger.info(
            f"AI Response Time: {end -start:.2f} seconds"
        )
        if not answer:
            answer ="Sorry , I couldn't process your request."
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