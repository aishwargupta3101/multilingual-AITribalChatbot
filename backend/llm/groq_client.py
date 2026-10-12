import json
import os
import time
from typing import Any, Dict, List
import httpx
from langchain_core.messages import AIMessage, BaseMessage
from backend.config.logger import logger

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def _convert_messages(messages: List[BaseMessage]) -> List[Dict[str, str]]:
    converted = []
    for message in messages:
        kind = getattr(message, "type", "")
        role = "system" if kind == "system" else "assistant" if kind == "ai" else "user"
        content = message.content
        if not isinstance(content, str):
            content = str(content)
        if content.strip():
            converted.append({"role": role, "content": content})
    return converted

class GroqLLM:
    """Hosted client with the same ainvoke/astream interface used by the current LlamaService."""
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY", "").strip()
        self.model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile").strip()
        self.timeout = float(os.getenv("GROQ_TIMEOUT_SECONDS", "180"))
        self.temperature = float(os.getenv("GROQ_TEMPERATURE", "0.3"))
        self.max_tokens = int(os.getenv("GROQ_MAX_TOKENS", "700"))
        self.top_p = os.getenv("GROQ_TOP_P", "").strip()
        if not self.api_key:
            raise RuntimeError("LLM_PROVIDER=groq but GROQ_API_KEY is missing. Add it to your private .env or set LLM_PROVIDER=ollama.")
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout, connect=20.0),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        )

    def _payload(self, messages, stream=False) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": _convert_messages(messages),
            "temperature": self.temperature,
            "max_completion_tokens": self.max_tokens,
            "stream": stream
        }
        if self.top_p:
            payload["top_p"] = float(self.top_p)
        return payload

    async def ainvoke(self, messages):
        payload = self._payload(messages)
        started = time.perf_counter()
        logger.info("Sending hosted LLM request | Provider: Groq | Model: %s | Messages: %s",
                    self.model, len(payload["messages"]))
        try:
            response = await self.client.post(GROQ_API_URL, json=payload)
            if response.is_error:
                logger.error("Groq API error %s: %s", response.status_code, response.text[:1000])
            response.raise_for_status()
            data = response.json()
            content = data["choices"][0]["message"].get("content") or ""
            if not content.strip():
                raise RuntimeError("Groq returned an empty response.")
            logger.info("Hosted LLM request completed in %.2f seconds.", time.perf_counter() - started)
            return AIMessage(content=content)
        except Exception:
            logger.exception("Hosted LLM request failed after %.2f seconds.", time.perf_counter() - started)
            raise

    async def astream(self, messages):
        payload = self._payload(messages, stream=True)
        started = time.perf_counter()
        first_token = True
        try:
            logger.info("GROQ_STREAM_START | model=%s | key_configured=%s",
                        self.model, bool(self.api_key))
            async with self.client.stream("POST", GROQ_API_URL, json=payload) as response:
                logger.info(
                    "GROQ_STREAM_CONNECTED | status_code=%s | model=%s",
                    response.status_code,
                    self.model,
                )
                if response.is_error:
                    body = await response.aread()
                    logger.error("Groq streaming API error %s: %s", response.status_code,
                                 body.decode("utf-8", errors="replace")[:1000])
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if not line or not line.startswith("data:"):
                        continue
                    raw = line[5:].strip()
                    if raw == "[DONE]":
                        break
                    try:
                        data = json.loads(raw)
                    except json.JSONDecodeError:
                        continue
                    choices = data.get("choices") or []
                    if not choices:
                        continue
                    content = (choices[0].get("delta") or {}).get("content")
                    if content:
                        if first_token:
                            logger.info("Hosted LLM first token in %.2f seconds.", time.perf_counter() - started)
                            first_token = False
                        yield AIMessage(content=content)
            logger.info("Hosted LLM stream completed in %.2f seconds.", time.perf_counter() - started)
        except Exception:
            logger.exception("Hosted LLM streaming failed after %.2f seconds.", time.perf_counter() - started)
            raise
