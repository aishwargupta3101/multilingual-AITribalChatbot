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
from backend.services.translation_service import translation_service


class ChatService:
    async def process_chat(
        self,
        request: ChatRequest
    ):
        logger.info("=" * 80)
        logger.info(f"Session ID : {request.session_id}")
        logger.info(f"Question   : {request.question}")
        original_question = request.question[:2000]
        translation_result = (
            translation_service.auto_translate_to_english(
                original_question
            )
        )
        question = translation_result["translated_text"]
        detected_language = translation_result["detected_language"]

        logger.info(f"Detected Language : {detected_language}")
        logger.info(f"Translated Question : {question}")
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
            role = message["role"]
            content = message["message"]
            if role =="user":
                language = message.get("language","english")
                if language.lower() != "english":

                    translation = translation_service.auto_translate_to_english(
                        text=content
                    )
                    content =translation["translated_text"]
            conversation.append(
                {
                    "role": role,
                    "content": content
                }
            )
        prompt = (
            "Please answer in English.\n\n"
            f"{question}"
        )

        context = ""
        sources = []
        if request.document_id:
            document = await document_repository.get_document_by_id(
                request.document_id
            )

        else:
            document = await document_repository.get_latest_document(
                request.session_id
            )

        logger.info(f"Document : {document}")
        if document:
            vector_db_path = document.get("vector_db_path")

            if vector_db_path:
                absolute_path = Path(vector_db_path).resolve()
                logger.info("=" * 80)
                logger.info(f"Vector DB : {absolute_path}")

                if absolute_path.exists():
                    logger.info("Loading RAG Context...")
                    rag_result = rag_service.build_context(
                        question=question,
                        vector_db_path=vector_db_path
                    )
                    context = rag_result.get(
                        "context",
                        ""
                    )
                    sources = rag_result.get(
                        "sources",
                        []
                    )
                    logger.info(
                        f"Context Length : {len(context)}"
                    )
                    logger.info(
                        f"Sources : {sources}"
                    )
                    if context.strip():

                        prompt = f"""
You are a helpful AI assistant.

Answer ONLY from the provided context.

If the answer is not present in the context, reply exactly:

I couldn't find that information in the uploaded document.

Always answer in English.

CONTEXT:
{context}

QUESTION:
{question}

ANSWER:
"""
                    else:
                        logger.warning(
                            "Retrieved context is empty."
                        )

                else:
                    logger.warning(
                        f"Vector database not found : {vector_db_path}"
                    )

        else:
            logger.info(
                "No uploaded document found."
            )
        logger.info("=" * 80)
        logger.info(prompt)
        logger.info("=" * 80)
        conversation.append(
            {
                "role": "user",
                "content": prompt
            }
        )
        await chat_repository.save_message(
            session_id=request.session_id,
            role="user",
            message=original_question,
            language=request.language
        )
        start = time.time()
        answer = await llama_service.generate_response(
            conversation
        )

        end = time.time()
        logger.info(
            f"LLM Response Time : {end - start:.2f} sec"
        )
        if not answer:
            answer = (
                "Sorry, I couldn't process your request."
            )
        if request.language.lower() != "english":
            answer = translation_service.translate_response(
                response=answer,
                user_language=request.language
            )
        await chat_repository.save_message(
            session_id=request.session_id,
            role="assistant",
            message=answer,
            language=request.language
        )
        logger.info("Chat completed successfully.")
        return ResponseBuilder.success(
            message="Chat processed successfully",
            data={
                "answer": answer,
                "language": request.language,
                "detected_language": detected_language,
                "sources": sources,
                "timestamp": str(datetime.now())
            }
        )
chat_service = ChatService()