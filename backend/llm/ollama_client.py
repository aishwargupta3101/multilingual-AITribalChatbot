from typing import Any, Dict, List

from ollama import AsyncClient
from langchain_core.messages import AIMessage, BaseMessage

from backend.config.settings import settings


def _convert_messages(messages: List[BaseMessage]) -> List[Dict[str, str]]:
    """
    Convert LangChain messages into Ollama message dictionaries.
    """

    converted = []

    for message in messages:
        if isinstance(message, AIMessage):
            role = "assistant"

        elif getattr(message, "type", None) == "system":
            role = "system"

        elif getattr(message, "type", None) == "human":
            role = "user"

        else:
            role = "user"

        content = message.content

        # Make sure content is a string
        if not isinstance(content, str):
            content = str(content)

        if content.strip():
            converted.append({
                "role": role,
                "content": content
            })

    return converted


class OllamaLLM:
    """
    Small compatibility wrapper around Ollama AsyncClient.

    This keeps the existing llama_service.py interface:
        await llm.ainvoke(...)
        async for chunk in llm.astream(...)
    """

    def __init__(self):
        base_url = settings.OLLAMA_BASE_URL.rstrip("/")

        headers = {}

        if settings.OLLAMA_PROXY_TOKEN:
            headers["Authorization"] = (
                f"Bearer {settings.OLLAMA_PROXY_TOKEN}"
            )

        self.client = AsyncClient(
            host=base_url,
            headers=headers,
            timeout=300.0
        )

        self.model = settings.LLAMA_MODEL

    def _options(self) -> Dict[str, Any]:
        """
        Map the existing project settings to Ollama options.
        """

        options = {}

        if hasattr(settings, "TEMPERATURE"):
            options["temperature"] = settings.TEMPERATURE

        if hasattr(settings, "TOP_P"):
            options["top_p"] = settings.TOP_P

        if hasattr(settings, "MAX_NEW_TOKEN"):
            options["num_predict"] = settings.MAX_NEW_TOKEN

        return options

    async def ainvoke(self, messages):
        """
        Non-streaming LLM response.
        """

        ollama_messages = _convert_messages(messages)

        response = await self.client.chat(
            model=self.model,
            messages=ollama_messages,
            stream=False,
            options=self._options()
        )

        return AIMessage(
            content=response.message.content
        )

    async def astream(self, messages):
        """
        Streaming LLM response.
        """

        ollama_messages = _convert_messages(messages)

        stream = await self.client.chat(
            model=self.model,
            messages=ollama_messages,
            stream=True,
            options=self._options()
        )

        async for chunk in stream:

            content = chunk.message.content

            if content:
                yield AIMessage(content=content)


llm = OllamaLLM()