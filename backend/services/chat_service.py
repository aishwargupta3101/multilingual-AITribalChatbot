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
from backend.rag.tai_khamti_rag import tai_khamti_rag
from backend.services.translation_service import translation_service


class ChatService:
    async def process_chat(self, request: ChatRequest):
        logger.info("=" * 80)
        logger.info(f"Session ID : {request.session_id}")
        logger.info(f"Question   : {request.question}")
        original_question = request.question[:2000]
        selected_language = request.language.lower().strip()

        logger.info(
            f"Selected Language : {selected_language}"
        )
        translation_result = (
            translation_service.auto_translate_to_english(
                original_question
            )
        )
        question = translation_result["translated_text"]
        detected_language = (
            translation_result["detected_language"]
        )
        logger.info(
            f"Detected Language : {detected_language}"
        )
        logger.info(
            f"Translated Question : {question}"
        )
        await session_repository.create_session(
            request.session_id
        )
        await session_repository.update_activity(
            request.session_id
        )
        history = await chat_repository.get_recent_message(
            request.session_id
        )
        conversation = []
        for message in history:
            role = message["role"]
            content = message["message"]

            if role == "user":
                language = message.get(
                    "language",
                    "english"
                )
                if language.lower() != "english":
                    translation = (
                        translation_service
                        .auto_translate_to_english(
                            content
                        )
                    )
                    content = translation[
                        "translated_text"
                    ]
            conversation.append(
                {
                    "role": role,
                    "content": content
                }
            )
        context = ""
        sources = []
        if request.document_id:

            document = (
                await document_repository
                .get_document_by_id(
                    request.document_id
                )
            )

        else:

            document = (
                await document_repository
                .get_latest_document(
                    request.session_id
                )
            )

        if document:

            vector_db_path = document.get(
                "vector_db_path"
            )

            if vector_db_path:

                absolute_path = (
                    Path(vector_db_path).resolve()
                )

                if absolute_path.exists():

                    logger.info(
                        "Loading uploaded document RAG..."
                    )

                    rag_result = (
                        rag_service.build_context(
                            question=question,
                            vector_db_path=vector_db_path
                        )
                    )

                    context = rag_result.get(
                        "context",
                        ""
                    )

                    sources = rag_result.get(
                        "sources",
                        []
                    )

        # ============================================================
        # 8. TAI KHAMTI VECTOR DATABASE
        #
        # IMPORTANT:
        # Tai Khamti RAG is used ONLY when the user selects
        # Tai Khamti.
        # ============================================================

        if (
            not context.strip()
            and selected_language in [
                "tai_khamti",
                "tai khamti"
            ]
        ):

            logger.info(
                "Searching Tai Khamti vector database..."
            )

            try:

                tai_khamti_rag_result = (
                    tai_khamti_rag.build_context(
                        question=question,
                        top_k=4,
                        language="tai_khamti"
                    )
                )

                tai_khamti_context = (
                    tai_khamti_rag_result.get(
                        "context",
                        ""
                    )
                )

                tai_khamti_sources = (
                    tai_khamti_rag_result.get(
                        "sources",
                        []
                    )
                )

                logger.info(
                    "Tai Khamti results found: "
                    f"{len(tai_khamti_sources)}"
                )
                if tai_khamti_context.strip():
                    context = tai_khamti_context
                    sources = tai_khamti_sources

            except Exception:
                logger.exception(
                    "Tai Khamti RAG search failed."
                )
        if selected_language in [
            "tai_khamti",
            "tai khamti"
        ]:
            if context.strip():
                prompt = f"""
You are a helpful AI assistant.

Answer ONLY in Tai Khamti.

IMPORTANT RULES:

1. Use the retrieved knowledge when relevant.
2. Do not invent facts.
3. Do not add unsupported information.
4. Answer naturally and directly.
5. Do not mention the knowledge base.
6. Do not say "According to the knowledge base".
7. Do not explain where the information came from.
8. Do not answer in English.
9. Give only the answer.

RETRIEVED KNOWLEDGE:

{context}

QUESTION:

{question}

ANSWER:
"""

            else:

                prompt = """
I could not find this information in the available knowledge.
"""
        elif selected_language == "hindi":
            if context.strip():
                prompt = f"""
You are a helpful AI assistant.

Answer ONLY in Hindi.

IMPORTANT RULES:

1. Use the retrieved knowledge when relevant.
2. Do not invent facts.
3. Do not add unsupported information.
4. Answer naturally and directly.
5. Do not mention the knowledge base.
6. Do not say "According to the knowledge base".
7. Do not explain where the information came from.
8. Give only the answer.

RETRIEVED KNOWLEDGE:

{context}

QUESTION:

{question}

ANSWER:
"""

            else:
                prompt = f"""
Answer the following question in Hindi.

Do not mention any knowledge base.

QUESTION:

{question}

ANSWER:
"""
        elif selected_language in [
            "manipuri",
            "mni_beng"
        ]:
            if context.strip():
                prompt = f"""
You are a helpful AI assistant.

Answer ONLY in Manipuri.

IMPORTANT RULES:

1. Use the retrieved knowledge when relevant.
2. Do not invent facts.
3. Do not add unsupported information.
4. Answer naturally and directly.
5. Do not mention the knowledge base.
6. Do not say "According to the knowledge base".
7. Do not explain where the information came from.
8. Give only the answer.

RETRIEVED KNOWLEDGE:

{context}

QUESTION:

{question}

ANSWER:
"""
            else:
                prompt = f"""
Answer the following question in Manipuri.

Do not mention any knowledge base.

QUESTION:

{question}

ANSWER:
"""
        else:
            if context.strip():

                prompt = f"""
You are a helpful AI assistant.

Answer ONLY in English.

IMPORTANT RULES:

1. Use the retrieved knowledge when relevant.
2. Do not invent facts.
3. Do not add unsupported information.
4. Answer naturally and directly.
5. Do not mention the knowledge base.
6. Do not say "According to the knowledge base".
7. Do not explain where the information came from.
8. Do not answer in another language.
9. Give only the answer.

RETRIEVED KNOWLEDGE:

{context}

QUESTION:

{question}

ANSWER:
"""
            else:
                prompt = f"""
You are a helpful AI assistant.

Answer ONLY in English.

IMPORTANT RULES:

1. Answer the user's question directly.
2. Do not invent facts.
3. Do not mention any knowledge base.
4. Do not provide unnecessary explanations.
5. Give only the answer.

QUESTION:

{question}

ANSWER:
"""
        logger.info(
            f"Final Context Length : {len(context)}"
        )
        logger.info(
            f"Sources : {sources}"
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
            message=original_question,
            language=request.language
        )
        start = time.time()

        answer = await llama_service.generate_response(
            conversation
        )
        end = time.time()
        logger.info(
            f"LLM Response Time : "
            f"{end - start:.2f} sec"
        )
        if not answer:

            answer = (
                "Sorry, I couldn't process your request."
            )
        if selected_language in [
            "tai_khamti",
            "tai khamti"
        ]:
            pass
        elif selected_language != "english":
            answer = (
                translation_service.translate_response(
                    response=answer,
                    user_language=request.language
                )
            )
        await chat_repository.save_message(
            session_id=request.session_id,
            role="assistant",
            message=answer,
            language=request.language
        )
        logger.info(
            "Chat completed successfully."
        )
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