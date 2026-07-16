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
    ):
        try:

            messages = [
                SystemMessage(content=SYSTEM_PROMPT)
            ]
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
            response = await llm.ainvoke(messages)

            if not response.content:
                return "Sorry, I couldn't generate a response."

            return response.content
        except Exception as error:
            logger.exception("Llama generation failed")
            return f"AI Error : {str(error)}"
    async def stream_response(
        self,
        conversation,
    ):
        messages = [
            SystemMessage(content=SYSTEM_PROMPT)
        ]
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
        async for chunk in llm.astream(messages):
            yield chunk.content

llama_service = LlamaService()