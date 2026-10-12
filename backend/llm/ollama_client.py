
import os
import time
from typing import Any, Dict, List

from ollama import AsyncClient
from langchain_core.messages import AIMessage, BaseMessage

from backend.config.settings import settings
from backend.config.logger import logger


def _convert_messages(messages: List[BaseMessage]) -> List[Dict[str, str]]:
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
        if not isinstance(content, str):
            content = str(content)
        if content.strip():
            converted.append({
                "role": role,
                "content": content
            })
    return converted

class OllamaLLM:
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
        options = {}
        if hasattr(settings, "TEMPERATURE"):
            options["temperature"] = settings.TEMPERATURE
        if hasattr(settings, "TOP_P"):
            options["top_p"] = settings.TOP_P
        if hasattr(settings, "MAX_NEW_TOKEN"):
            options["num_predict"] = settings.MAX_NEW_TOKEN
        # Local benchmark showed better throughput with 10 CPU threads.
        try:
            options["num_thread"] = max(1, int(os.getenv("OLLAMA_NUM_THREAD", "10")))
        except (TypeError, ValueError):
            options["num_thread"] = 10
        return options
    async def ainvoke(self, messages):
        ollama_messages = _convert_messages(messages)
        prompt_chars = sum(
            len(message["content"])
            for message in ollama_messages
        )
        logger.info(
            "Sending Ollama request | Model: %s | Messages: %s | Prompt characters: %s",
            self.model,
            len(ollama_messages),
            prompt_chars
        )
        start_time = time.time()

        try:

            response = await self.client.chat(
                model=self.model,
                messages=ollama_messages,
                stream=False,
                options=self._options(),
                keep_alive="30m",
            )

            elapsed = time.time() - start_time

            prompt_tokens = getattr(response, "prompt_eval_count", 0) or 0
            generated_tokens = getattr(response, "eval_count", 0) or 0
            prompt_duration = getattr(response, "prompt_eval_duration", 0) or 0
            generation_duration = getattr(response, "eval_duration", 0) or 0
            total_duration = getattr(response, "total_duration", 0) or 0

            prompt_seconds = prompt_duration / 1e9
            generation_seconds = generation_duration / 1e9
            total_seconds = total_duration / 1e9

            tokens_per_second = (
                generated_tokens / generation_seconds
                if generation_seconds > 0 else 0
            )

            logger.info(
                f"Ollama performance | "
                f"Elapsed: {elapsed:.2f}s | "
                f"Total: {total_seconds:.2f}s | "
                f"Prompt: {prompt_seconds:.2f}s ({prompt_tokens} tokens) | "
                f"Generation: {generation_seconds:.2f}s ({generated_tokens} tokens) | "
                f"Speed: {tokens_per_second:.2f} tokens/sec"
            )

            return AIMessage(
                content=response.message.content
            )
        except Exception:
            logger.exception(
                "Ollama request failed after %.2f seconds.",
                time.time() - start_time
            )
            raise


    async def astream(self, messages):
        ollama_messages = _convert_messages(messages)

        start_time = time.time()

        stream = await self.client.chat(
            model=self.model,
            messages=ollama_messages,
            stream=True,
            options=self._options(),
            keep_alive="30m"
        )

        async for chunk in stream:
            content = chunk.message.content

            if content:
                yield AIMessage(content=content)

            if getattr(chunk, "done", False):
                elapsed = time.time() - start_time

                prompt_tokens = getattr(
                    chunk, "prompt_eval_count", 0
                ) or 0

                generated_tokens = getattr(
                    chunk, "eval_count", 0
                ) or 0

                prompt_duration = getattr(
                    chunk, "prompt_eval_duration", 0
                ) or 0

                generation_duration = getattr(
                    chunk, "eval_duration", 0
                ) or 0

                total_duration = getattr(
                    chunk, "total_duration", 0
                ) or 0

                prompt_seconds = prompt_duration / 1e9
                generation_seconds = generation_duration / 1e9
                total_seconds = total_duration / 1e9

                tokens_per_second = (
                    generated_tokens / generation_seconds
                    if generation_seconds > 0 else 0
                )

                logger.info(
                    f"Ollama streaming performance | "
                    f"Elapsed: {elapsed:.2f}s | "
                    f"Total: {total_seconds:.2f}s | "
                    f"Prompt: {prompt_seconds:.2f}s ({prompt_tokens} tokens) | "
                    f"Generation: {generation_seconds:.2f}s ({generated_tokens} tokens) | "
                    f"Speed: {tokens_per_second:.2f} tokens/sec"
                )
llm = OllamaLLM()