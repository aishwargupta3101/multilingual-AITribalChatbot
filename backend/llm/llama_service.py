from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    AIMessage
)

from backend.llm.ollama_client import llm
from backend.llm.prompt import SYSTEM_PROMPT
from backend.config.logger import logger

class LlamaService:
    async def generate_response(
        self,
        conversation,
        rag_context=None
    ):
        try:
            messages = [
                SystemMessage(
                    content=SYSTEM_PROMPT
                )
            ]
            if rag_context and rag_context.strip():

                rag_message = f"""
You have access to the following retrieved knowledge.

Use this knowledge when it is relevant to the user's question.
Do not invent information that is not present in the knowledge.
RETRIEVED KNOWLEDGE:
{rag_context}
END OF RETRIEVED KNOWLEDGE.
"""
                messages.append(
                    SystemMessage(
                        content=rag_message
                    )
                )
            for item in conversation:
                if item["role"] == "user":
                    messages.append(
                        HumanMessage(
                            content=item["content"]
                        )
                    )
                elif item["role"] == "assistant":
                    messages.append(
                        AIMessage(
                            content=item["content"]
                        )
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
            messages = [
                SystemMessage(
                    content=SYSTEM_PROMPT
                )
            ]
            if rag_context and rag_context.strip():
                rag_message = f"""
You have access to the following retrieved knowledge.
Use this knowledge when it is relevant to the user's question.
Do not invent information that is not present in the knowledge.

RETRIEVED KNOWLEDGE:
{rag_context}
END OF RETRIEVED KNOWLEDGE.
"""

                messages.append(
                    SystemMessage(
                        content=rag_message
                    )
                )
            for item in conversation:
                if item["role"] == "user":
                    messages.append(
                        HumanMessage(
                            content=item["content"]
                        )
                    )
                elif item["role"] == "assistant":
                    messages.append(
                        AIMessage(
                            content=item["content"]
                        )
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