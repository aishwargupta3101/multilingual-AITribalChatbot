from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage
)
from backend.llm.ollama_client import llm
from backend.llm.prompt import SYSTEM_PROMPT
from backend.config.logger import logger


class LlamaService:
    def _build_messages(
        self,
        conversation,
        rag_context=None
    ):
        """
        Build messages efficiently.

        Only the recent conversation history is sent
        to the LLM to reduce input token processing.
        """
        messages = [
            SystemMessage(
                content=SYSTEM_PROMPT
            )
        ]
        if rag_context and rag_context.strip():
            rag_message = (
                "Use the following retrieved knowledge "
                "when relevant.\n"
                "Do not invent information that is not "
                "present in the knowledge.\n\n"
                "RETRIEVED KNOWLEDGE:\n"
                f"{rag_context.strip()}\n"
                "END OF RETRIEVED KNOWLEDGE."
            )
            messages.append(
                SystemMessage(
                    content=rag_message
                )
            )
        recent_conversation = conversation[-6:]

        for item in recent_conversation:
            role = item.get("role")
            content = item.get("content", "").strip()
            if not content:
                continue
            if role == "user":
                messages.append(
                    HumanMessage(
                        content=content
                    )
                )
            elif role == "assistant":
                messages.append(
                    AIMessage(
                        content=content
                    )
                )
        return messages

    async def generate_response(
        self,
        conversation,
        rag_context=None
    ):
        try:
            messages = self._build_messages(
                conversation,
                rag_context
            )
            response = await llm.ainvoke(
                messages
            )
            if not response.content:
                return (
                    "Sorry, I couldn't generate "
                    "a response."
                )
            return response.content

        except Exception as error:
            logger.exception(
                "Llama generation failed"
            )
            return f"AI Error : {str(error)}"

    async def stream_response(
        self,
        conversation,
        rag_context=None
    ):
        try:
            messages = self._build_messages(
                conversation,
                rag_context
            )
            async for chunk in llm.astream(
                messages
            ):
                if chunk.content:
                    yield chunk.content

        except Exception as error:
            logger.exception(
                "Llama streaming failed"
            )
            yield f"AI Error : {str(error)}"
llama_service = LlamaService()