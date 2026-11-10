"""LLM provider selection with automatic Ollama fallback for Groq failures.

LlamaService continues to use the same `llm.ainvoke()` and `llm.astream()` API.
Set LLM_PROVIDER=groq to prefer Groq. If Groq errors or returns empty output,
requests fall back to the configured Ollama model when enabled.
"""
import os
from typing import Any

from backend.config.logger import logger
from backend.config.settings import settings


def _enabled(name: str, default: bool = True) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


_PROVIDER = str(settings.LLM_PROVIDER or "ollama").strip().lower()
_FALLBACK_ENABLED = settings.LLM_FALLBACK_TO_OLLAMA

if _PROVIDER == "groq":
    from backend.llm.groq_client import GroqLLM

    try:
        _primary_llm = GroqLLM()
        logger.info("LLM provider selected: Groq hosted inference.")
    except Exception:
        if not _FALLBACK_ENABLED:
            raise
        logger.exception("Groq could not initialize; selecting Ollama fallback.")
        from backend.llm.ollama_client import OllamaLLM
        _primary_llm = OllamaLLM()
        llm = _primary_llm
    else:
        if _FALLBACK_ENABLED:
            from backend.llm.ollama_client import OllamaLLM

            class ResilientLLM:
                """Use Groq first and Ollama if Groq fails or returns no text."""
                def __init__(self, primary: Any, fallback: Any):
                    self.primary = primary
                    self.fallback = fallback
                    self._using_fallback = False

                async def ainvoke(self, messages):
                    if self._using_fallback:
                        return await self.fallback.ainvoke(messages)
                    try:
                        result = await self.primary.ainvoke(messages)
                        content = getattr(result, "content", "")
                        if not (content if isinstance(content, str) else str(content)).strip():
                            raise RuntimeError("Groq returned an empty response.")
                        return result
                    except Exception:
                        logger.exception("Groq generation failed; retrying this request with Ollama.")
                        result = await self.fallback.ainvoke(messages)
                        content = getattr(result, "content", "")
                        if not (content if isinstance(content, str) else str(content)).strip():
                            raise RuntimeError("Ollama fallback returned an empty response.")
                        self._using_fallback = True
                        logger.warning("LLM provider switched to Ollama after Groq failure.")
                        return result

                async def astream(self, messages):
                    if self._using_fallback:
                        async for chunk in self.fallback.astream(messages):
                            if getattr(chunk, "content", None):
                                yield chunk
                        return

                    # Buffer Groq's stream until completion. This avoids sending
                    # partial Groq text and then duplicating it with Ollama output
                    # if Groq fails halfway through generation.
                    buffered = []
                    try:
                        async for chunk in self.primary.astream(messages):
                            if getattr(chunk, "content", None):
                                buffered.append(chunk)
                        if not buffered:
                            raise RuntimeError("Groq streaming returned no text.")
                        for chunk in buffered:
                            yield chunk
                    except Exception:
                        logger.exception("Groq streaming failed; retrying with Ollama.")
                        self._using_fallback = True
                        async for chunk in self.fallback.astream(messages):
                            if getattr(chunk, "content", None):
                                yield chunk
                        logger.warning("LLM provider switched to Ollama after Groq streaming failure.")

            llm = ResilientLLM(_primary_llm, OllamaLLM())
        else:
            llm = _primary_llm
else:
    from backend.llm.ollama_client import OllamaLLM
    llm = OllamaLLM()
    logger.info("LLM provider selected: local Ollama.")
