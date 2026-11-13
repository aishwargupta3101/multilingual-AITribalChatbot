from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage
)
from backend.llm.groq_client import GroqLLM
llm = GroqLLM()
from backend.llm.prompt import SYSTEM_PROMPT
from backend.config.logger import logger

MAX_HISTORY_MESSAGES = 8
MAX_RAG_CONTEXT_CHARS = 3000


class LlamaService:
    def _build_messages(self, conversation, rag_context=None, system_prompt=None):
        # Task-specific instructions are supplied by ChatService as a system
        # message. Keep the shared base prompt for all existing callers.
        combined_system_prompt = SYSTEM_PROMPT.rstrip()
        if system_prompt and str(system_prompt).strip():
            combined_system_prompt += "\n\n" + str(system_prompt).strip()
        messages = [SystemMessage(content=combined_system_prompt)]

        if rag_context and rag_context.strip():
            rag_context = rag_context.strip()[:MAX_RAG_CONTEXT_CHARS]
            rag_message = (
                "Use the following retrieved knowledge "
                "when relevant.\n"
                "Do not invent information that is not "
                "present in the knowledge.\n\n"
                "RETRIEVED KNOWLEDGE:\n"
                f"{rag_context}\n"
                "END OF RETRIEVED KNOWLEDGE."
            )
            messages.append(SystemMessage(content=rag_message))

        recent_conversation = conversation[-MAX_HISTORY_MESSAGES:]

        for item in recent_conversation:
            role = item.get("role")
            content = item.get("content", "")

            if not isinstance(content, str):
                content = str(content)

            content = content.strip()

            if not content:
                continue
            if role == "assistant" and content.lower().startswith("ai error"):
                logger.warning("Skipping failed assistant response from history.")
                continue

            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))

        total_chars = sum(
            len(str(message.content))
            for message in messages
        )

        logger.info(
            "LLM prompt prepared | Messages: %s | Total characters: %s | RAG characters: %s",
            len(messages),
            total_chars,
            len(rag_context) if rag_context else 0
        )

        return messages

    async def generate_response(self, conversation, rag_context=None, system_prompt=None):
        messages = self._build_messages(conversation, rag_context, system_prompt)

        try:
            response = await llm.ainvoke(messages)

            if not response.content:
                raise ValueError("LLM returned an empty response.")

            return response.content

        except Exception:
            logger.exception("Llama generation failed.")
            raise

    async def stream_response(self, conversation, rag_context=None, system_prompt=None):
        messages = self._build_messages(conversation, rag_context, system_prompt)

        try:
            async for chunk in llm.astream(messages):
                if chunk.content:
                    yield chunk.content

        except Exception:
            logger.exception("Llama streaming failed.")
            raise
llama_service = LlamaService()
