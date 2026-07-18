from datetime import datetime
import time
from pathlib import Path
from backend.schemas.chat import ChatRequest
from backend.utils.response import ResponseBuilder
from backend.config.logger import logger
from backend.repositories.chat_repository import chat_repository
from backend.repositories.session_repository import session_repository
from backend.repositories.document_repository import document_repository
from backend.llm.llama_service import llama_service
from backend.rag.rag_service import rag_service


class ChatService:

    async def process_chat(
        self,
        request: ChatRequest
    ):
        logger.info(
            f"Session: {request.session_id}"
        )
        logger.info(
            f"Question: {request.question}"
        )
        question = request.question[:2000]
        await session_repository.create_session(
            request.session_id
        )
        await session_repository.update_activity(
            request.session_id
        )
        history = await chat_repository.get_recent_message(
            request.session_id
        )
        logger.info(
            f"Loaded {len(history)} previous messages"
        )
        conversation = []
        for message in history:
            conversation.append(
                {
                    "role": message["role"],
                    "content": message["message"]
                }
            )
        prompt = (
            f"Please answer in {request.language}.\n\n"
            f"{question}"
        )

        context = ""
        sources = []
        document = None

        if request.document_id:
            document = await document_repository.get_document_by_id(
                request.document_id
            )
        else:
            document = await document_repository.get_latest_document(
                request.session_id
            )
        if document:
            vector_db_path = document["vector_db_path"]
            if Path(vector_db_path).exists():
                logger.info(
                    f"Using vector database: {vector_db_path}"
                )
                rag_result = rag_service.build_context(
                    question=question,
                    vector_db_path=vector_db_path
                )
                context = rag_result["context"]
                sources = rag_result["sources"]
                if context.strip():
                    prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the provided context.

If the answer is not available in the context, reply exactly:

I couldn't find that information in the uploaded document.

Always respond in {request.language}.

Context:
{context}

Question:
{question}

Answer:
"""
            else:

                logger.warning(
                    f"Vector database not found: {vector_db_path}"
                )
        else:
            logger.info(
                "No uploaded document found. Using normal LLM."
            )
        conversation.append(
            {
                "role": "user",
                "content": prompt
            }
        )
        await chat_repository.save_message(
            session_id=request.session_id,
            role="user",
            message=question,
            language=request.language,
        )
        start = time.time()
        answer = await llama_service.generate_response(
            conversation
        )
        end = time.time()
        logger.info(
            f"AI Response Time: {end - start:.2f} seconds"
        )
        if not answer:
            answer = "Sorry, I couldn't process your request."
        await chat_repository.save_message(
            session_id=request.session_id,
            role="assistant",
            message=answer,
            language=request.language,
        )
        logger.info(
            "Chat response generated successfully."
        )
        return ResponseBuilder.success(
            message="Chat processed successfully",
            data={
                "answer": answer,
                "language": request.language,
                "sources": sources,
                "timestamp": str(datetime.now())
            }
        )
chat_service = ChatService()