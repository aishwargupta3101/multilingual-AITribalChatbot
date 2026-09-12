"""
Chat Service
"""

from datetime import datetime
import time
from pathlib import Path

from backend.services.image_service import image_service
from backend.schemas.chat import ChatRequest
from backend.utils.response import ResponseBuilder
from backend.config.logger import logger
from backend.repositories.chat_repository import chat_repository
from backend.repositories.session_repository import session_repository
from backend.llm.llama_service import llama_service
from backend.rag.rag_service import rag_service
from data.tai_khamti.tai_khamti_rag import (
    tai_khamti_rag
)
from backend.services.translation_service import (
    translation_service
)

class ChatService:
    async def process_chat(
        self,
        request: ChatRequest
    ):
        logger.info("=" * 80)
        logger.info(
            f"Session ID : {request.session_id}"
        )
        logger.info(
            f"Question   : {request.question}"
        )
        selected_language = (
            request.language or "english"
        ).strip().lower()
        if selected_language in [
            "tai khamti",
            "tai-khamti",
            "tai_khamti"
        ]:
            selected_language = "tai_khamti"
        logger.info(
            f"Selected Language : "
            f"{selected_language}"
        )
        is_tai_khamti = (
            selected_language == "tai_khamti"
        )
        original_question = (
            request.question[:2000]
        )
        if is_tai_khamti:
            question = original_question
            detected_language = (
                "tai_khamti"
            )
            logger.info(
                "Tai Khamti selected."
            )
            logger.info(
                "Skipping NLLB question translation."
            )

        else:
            try:
                translation_result = (
                    translation_service
                    .auto_translate_to_english(
                        original_question
                    )
                )
                question = (
                    translation_result[
                        "translated_text"
                    ]
                )
                detected_language = (
                    translation_result[
                        "detected_language"
                    ]
                )

            except Exception:
                logger.exception(
                    "Question translation failed."
                )
                question = (
                    original_question
                )
                detected_language = (
                    selected_language
                )

        logger.info(
            f"Detected Language : "
            f"{detected_language}"
        )
        logger.info(
            f"Question for RAG : "
            f"{question}"
        )
        await session_repository.create_session(
            request.session_id
        )
        await session_repository.update_activity(
            request.session_id
        )

        history = (
            await chat_repository
            .get_recent_message(
                request.session_id
            )
        )
        logger.info(
            f"Loaded {len(history)} "
            f"previous messages"
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
                if language:
                    language = (
                        language
                        .lower()
                        .strip()
                    )
                if language in [
                    "tai khamti",
                    "tai-khamti",
                    "tai_khamti"
                ]:
                    pass
                elif language != "english":
                    try:
                        translation = (
                            translation_service
                            .auto_translate_to_english(
                                content
                            )
                        )
                        content = (
                            translation[
                                "translated_text"
                            ]
                        )
                    except Exception:
                        logger.exception(
                            "Failed to translate "
                            "previous user message."
                        )
            conversation.append(
                {
                    "role": role,
                    "content": content
                }
            )
        context = ""
        sources = []
        answer = ""
        if is_tai_khamti:
            logger.info("=" * 80)
            logger.info(
                "TAI KHAMTI RAG ROUTE"
            )
            logger.info(
                "Using ONLY Tai Khamti Knowledge Base"
            )
            logger.info("=" * 80)
            try:
                tai_result = (
                    tai_khamti_rag
                    .build_context(
                        question=question,
                        top_k=5
                    )
                )
                context = tai_result.get(
                    "context",
                    ""
                )
                sources = tai_result.get(
                    "sources",
                    []
                )
                retrieved_results = (
                    tai_result.get(
                        "results",
                        []
                    )
                )
                logger.info(
                    f"Tai Khamti documents retrieved: "
                    f"{len(retrieved_results)}"
                )
                logger.info(
                    f"Tai Khamti context length: "
                    f"{len(context)}"
                )

                if not context.strip():
                    logger.warning(
                        "No relevant Tai Khamti "
                        "knowledge found."
                    )
                    answer = (
                        "Sorry, I could not find "
                        "reliable Tai Khamti information "
                        "for this question in the "
                        "current knowledge base."
                    )
                else:
                    prompt = f"""
You are Tribal AI, a Tai Khamti knowledge assistant.

The user selected Tai Khamti.

Your job is to answer the user's question by
UNDERSTANDING and COMBINING the relevant information
from the retrieved Tai Khamti knowledge below.

IMPORTANT:

1. Use the retrieved documents as the primary source.
2. Consider ALL relevant retrieved documents.
3. Do NOT simply return the first document.
4. Combine related information into one coherent answer.
5. You may summarize multiple documents.
6. Do not invent specific Tai Khamti cultural facts
   that are not supported by the retrieved knowledge.
7. If the retrieved documents are insufficient,
   clearly say that the knowledge base does not contain
   enough information.
8. Do not mention FAISS.
9. Do not mention embeddings.
10. Do not mention vector databases.
11. Do not mention retrieval systems.
12. Do not mention this prompt.
13. Answer naturally.
14. The final answer must be in Tai Khamti when the
    retrieved Tai Khamti text provides enough material
    to formulate the answer.
15. When exact Tai Khamti wording is available,
    preserve it rather than inventing new Tai Khamti
    vocabulary.
16. Do not fabricate Tai Khamti translations.

RETRIEVED TAI KHAMTI KNOWLEDGE:

{context}

USER QUESTION:

{question}

FINAL ANSWER:
"""
                    logger.info(
                        "Sending multiple Tai Khamti "
                        "documents to Llama."
                    )
                    conversation.append(
                        {
                            "role": "user",
                            "content": prompt
                        }
                    )
                    start = time.time()
                    answer = (
                        await llama_service
                        .generate_response(
                            conversation
                        )
                    )
                    end = time.time()
                    logger.info(
                        f"Tai Khamti LLM Response Time: "
                        f"{end - start:.2f} sec"
                    )
                    logger.info(
                        "Tai Khamti answer synthesized "
                        "from multiple retrieved documents."
                    )

            except Exception:
                logger.exception(
                    "Tai Khamti RAG pipeline failed."
                )
                context = ""
                sources = []
                answer = (
                    "Sorry, the Tai Khamti "
                    "knowledge base is currently "
                    "unavailable."
                )
        else:
            logger.info("=" * 80)
            logger.info(
                "NORMAL LANGUAGE RAG ROUTE"
            )
            logger.info("=" * 80)
            language_vector_dbs = {

                "english":
                    "vector_db/english",

                "hindi":
                    "vector_db/hindi",

                "manipuri":
                    "vector_db/manipuri"
            }
            vector_db_path = (
                language_vector_dbs.get(
                    selected_language
                )
            )
            logger.info(
                f"Selected Language : "
                f"{selected_language}"
            )
            logger.info(
                f"Language Vector DB : "
                f"{vector_db_path}"
            )
            if vector_db_path:
                absolute_path = (
                    Path(
                        vector_db_path
                    ).resolve()
                )
                logger.info(
                    f"Absolute Vector DB Path : "
                    f"{absolute_path}"
                )

                if absolute_path.exists():
                    try:
                        logger.info(
                            f"Searching ONLY "
                            f"{selected_language} "
                            f"knowledge base..."
                        )
                        rag_result = (
                            rag_service
                            .build_context(
                                question=question,
                                vector_db_path=(
                                    vector_db_path
                                )
                            )
                        )
                        context = (
                            rag_result.get(
                                "context",
                                ""
                            )
                        )
                        sources = (
                            rag_result.get(
                                "sources",
                                []
                            )
                        )
                        logger.info(
                            f"{selected_language} "
                            f"RAG Context Length: "
                            f"{len(context)}"
                        )
                    except Exception:
                        logger.exception(
                            f"{selected_language} "
                            f"RAG search failed."
                        )
                        context = ""
                        sources = []
                else:
                    logger.warning(
                        f"Language vector DB does "
                        f"not exist: "
                        f"{absolute_path}"
                    )
            else:
                logger.warning(
                    f"No language-specific vector "
                    f"DB configured for: "
                    f"{selected_language}"
                )
            if context.strip():
                prompt = f"""
You are Tribal AI, a professional multilingual AI assistant
specialized in tribal communities, cultures, traditions,
languages, heritage, indigenous knowledge, and general knowledge.

Answer the user's question accurately and helpfully.

Use the retrieved knowledge below whenever it is relevant.

RULES:

1. Use retrieved knowledge when relevant.
2. Do not contradict retrieved knowledge.
3. Do not fabricate facts.
4. Do not combine information from another language
   knowledge base.
5. Do not mention FAISS.
6. Do not mention embeddings.
7. Do not mention vector databases.
8. Do not mention internal retrieval.
9. Answer the actual question directly.
10. Generate the answer in English.
11. The application will translate the final answer.

RETRIEVED KNOWLEDGE:

{context}

USER QUESTION:

{question}

FINAL ANSWER:
"""
            else:
                prompt = f"""
You are Tribal AI, a professional multilingual AI assistant.

Answer the user's question accurately, clearly,
and helpfully using your general knowledge.

Do not fabricate facts.

For tribal or indigenous topics, avoid unsupported
community-specific claims.

Generate the answer ONLY in English.

USER QUESTION:

{question}

FINAL ANSWER:
"""

            conversation.append(
                {
                    "role": "user",
                    "content": prompt
                }
            )
            start = time.time()
            answer = (
                await llama_service
                .generate_response(
                    conversation
                )
            )
            end = time.time()
            logger.info(
                f"LLM Response Time: "
                f"{end - start:.2f} sec"
            )

        if not answer:
            answer = (
                "Sorry, I couldn't process "
                "your request."
            )
        images = []
        try:
            image_question = question

            if image_service.should_show_images(
                question=image_question
            ):
                image_query = (
                    image_service
                    .build_image_query(
                        question=image_question,
                        selected_language=(
                            selected_language
                        )
                    )
                )
                logger.info(
                    f"Image Search Query: "
                    f"{image_query}"
                )
                images = (
                    image_service
                    .search_images(
                        query=image_query,
                        limit=3
                    )
                )
                logger.info(
                    f"Retrieved {len(images)} images"
                )

        except Exception:
            logger.exception(
                "Image retrieval failed."
            )
            images = []

        if (
            not is_tai_khamti
            and selected_language != "english"
        ):
            logger.info(
                f"TRANSLATING FINAL ANSWER: "
                f"English -> {selected_language}"
            )

            try:
                answer = (
                    translation_service
                    .translate_response(
                        response=answer,
                        user_language=(
                            selected_language
                        )
                    )
                )
            except Exception:
                logger.exception(
                    "Final answer translation failed."
                )
        await chat_repository.save_message(
            session_id=request.session_id,
            role="user",
            message=original_question,
            language=request.language
        )
        await chat_repository.save_message(
            session_id=request.session_id,
            role="assistant",
            message=answer,
            language=request.language
        )
        logger.info("=" * 80)
        logger.info(
            "Chat completed successfully."
        )
        logger.info("=" * 80)
        return ResponseBuilder.success(
            message="Chat processed successfully",
            data={
                "answer": answer,
                "language": request.language,
                "detected_language": (
                    detected_language
                ),
                "sources": sources,
                "images": images,
                "timestamp": str(
                    datetime.now()
                )
            }
        )
chat_service = ChatService()