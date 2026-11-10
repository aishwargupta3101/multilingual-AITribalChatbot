import json
import os
import time
from typing import Any, Dict, List
import httpx
import asyncio
from langchain_core.messages import AIMessage, BaseMessage
from backend.config.logger import logger
from backend.config.settings import settings
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

def _extract_message_text(message: Any) -> str:
    """Extract text from standard and block-based OpenAI-compatible responses."""
    if not isinstance(message, dict):
        return ""
    content = message.get("content")
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "".join(parts).strip()
    return ""

class GroqLLM:
    def __init__(self, api_key: str | None = None):
        self.api_key = (
                api_key or settings.GROQ_API_KEY
        ).strip()

        self.model = settings.GROQ_MODEL.strip()
        self.timeout = settings.GROQ_TIMEOUT_SECONDS
        self.temperature = settings.GROQ_TEMPERATURE
        self.max_tokens = settings.GROQ_MAX_TOKENS
        self.top_p = (
            str(settings.GROQ_TOP_P)
            if settings.GROQ_TOP_P is not None
            else ""
        )
        if not self.api_key:
            raise RuntimeError("Groq API key is missing.")

        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout, connect=20.0),
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
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
        max_retries = 1
        max_retry_wait = 5.0

        logger.info(
            "Sending hosted LLM request | Provider: Groq | Model: %s | Messages: %s",
            self.model,
            len(payload["messages"]),
        )

        for attempt in range(max_retries + 1):
            try:
                response = await self.client.post(
                    GROQ_API_URL,
                    json=payload,
                )

                if response.status_code == 429 and attempt < max_retries:
                    retry_after = response.headers.get("retry-after", "")

                    try:
                        wait_seconds = float(retry_after)
                    except (TypeError, ValueError):
                        wait_seconds = 0

                    if 0 < wait_seconds <= max_retry_wait:
                        logger.warning(
                            "Groq rate limited request. Retrying once in %.1f seconds.",
                            wait_seconds,
                        )
                        await asyncio.sleep(wait_seconds)
                        continue

                    logger.warning(
                        "Groq returned 429 without a short Retry-After value. "
                        "Skipping retry so provider fallback can run."
                    )

                if response.is_error:
                    diagnostic_headers = {
                        name: response.headers.get(name)
                        for name in (
                            "retry-after",
                            "x-ratelimit-limit-requests",
                            "x-ratelimit-remaining-requests",
                            "x-ratelimit-reset-requests",
                            "x-ratelimit-limit-tokens",
                            "x-ratelimit-remaining-tokens",
                            "x-ratelimit-reset-tokens",
                        )
                        if response.headers.get(name) is not None
                    }

                    logger.error(
                        "Groq API error | status=%s | headers=%s | body=%s",
                        response.status_code,
                        diagnostic_headers,
                        response.text[:1000],
                    )

                response.raise_for_status()

                data = response.json()
                choices = data.get("choices") or []
                message = choices[0].get("message") or {} if choices else {}
                content = _extract_message_text(message)

                if not content.strip():
                    raise RuntimeError("Groq returned an empty response.")

                logger.info(
                    "Groq request completed in %.2f seconds.",
                    time.perf_counter() - started,
                )
                return AIMessage(content=content)

            except Exception:
                logger.exception(
                    "Groq generation failed on attempt %s.",
                    attempt + 1,
                )
                raise

        raise RuntimeError("Groq request failed after retry.")

    async def astream(self, messages):
        payload = self._payload(messages, stream=True)
        started = time.perf_counter()
        first_token = True
        yielded_any = False
        try:
            logger.info(
                "GROQ_STREAM_START | model=%s | key_configured=%s | messages=%s",
                self.model, bool(self.api_key), len(payload["messages"])
            )
            async with self.client.stream("POST", GROQ_API_URL, json=payload) as response:
                logger.info(
                    "GROQ_STREAM_CONNECTED | status_code=%s | model=%s",
                    response.status_code, self.model
                )
                if response.is_error:
                    body = await response.aread()
                    logger.error(
                        "Groq streaming API error %s: %s",
                        response.status_code,
                        body.decode("utf-8", errors="replace")[:1000]
                    )
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
                            logger.info(
                                "Hosted LLM first token in %.2f seconds.",
                                time.perf_counter() - started
                            )
                            first_token = False
                        yielded_any = True
                        yield AIMessage(content=content)
            if not yielded_any:
                raise RuntimeError("Groq streaming completed without returning any text.")
            logger.info("Hosted LLM stream completed in %.2f seconds.", time.perf_counter() - started)
        except Exception:
            logger.exception(
                "Hosted LLM streaming failed after %.2f seconds.",
                time.perf_counter() - started
            )
            if yielded_any:
                raise
            logger.warning("Retrying Groq request without streaming.")
            try:
                fallback_payload = dict(payload)
                fallback_payload["stream"] = False
                response = await self.client.post(
                    GROQ_API_URL,
                    json=fallback_payload
                )
                if response.is_error:
                    logger.error(
                        "Groq non-streaming fallback API error %s: %s",
                        response.status_code, response.text[:1000]
                    )
                response.raise_for_status()
                data = response.json()
                choices = data.get("choices") or []
                message = (choices[0].get("message") or {}) if choices else {}
                content = _extract_message_text(message)
                if not content:
                    finish_reason = choices[0].get("finish_reason") if choices else None
                    logger.warning(
                        "Groq fallback returned empty text | finish_reason=%s | choice_count=%s | response_keys=%s",
                        finish_reason, len(choices), sorted(data.keys()) if isinstance(data, dict) else []
                    )
                    retry_payload = dict(fallback_payload)
                    retry_payload["max_completion_tokens"] = max(self.max_tokens, 1024)
                    retry_response = await self.client.post(GROQ_API_URL, json=retry_payload)
                    if retry_response.is_error:
                        logger.error(
                            "Groq empty-response retry API error %s: %s",
                            retry_response.status_code, retry_response.text[:1000]
                        )
                    retry_response.raise_for_status()
                    retry_data = retry_response.json()
                    retry_choices = retry_data.get("choices") or []
                    retry_message = (retry_choices[0].get("message") or {}) if retry_choices else {}
                    content = _extract_message_text(retry_message)
                    if not content:
                        retry_reason = retry_choices[0].get("finish_reason") if retry_choices else None
                        raise RuntimeError(
                            "Groq returned no text after the non-streaming retry "
                            f"(finish_reason={retry_reason!r}, choices={len(retry_choices)})."
                        )
                logger.info(
                    "Groq non-streaming fallback succeeded in %.2f seconds.",
                    time.perf_counter() - started
                )
                yield AIMessage(content=content)
            except Exception:
                logger.exception("Groq non-streaming fallback failed.")
                raise
