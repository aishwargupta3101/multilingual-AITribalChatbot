"""Education LLM client with Gemini -> OpenRouter -> local Ollama fallback.

Maintains the existing EducationGeminiClient.ainvoke(prompt) interface, so the
education lesson/quiz/worksheet router does not need to change.
"""
import asyncio
import os
from typing import Any

import httpx
from backend.config.logger import logger


class EducationGeminiClient:
    """Backward-compatible education model client with provider fallbacks."""

    def __init__(self) -> None:
        self.gemini_api_key = os.getenv("EDUCATION_GEMINI_API_KEY", "").strip()
        self.gemini_model = os.getenv("EDUCATION_GEMINI_MODEL", "gemini-2.5-flash").strip()
        self.timeout = float(os.getenv("EDUCATION_GEMINI_TIMEOUT_SECONDS", "120"))

        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        self.openrouter_model = os.getenv("EDUCATION_OPENROUTER_MODEL", "openrouter/free").strip()
        self.openrouter_url = os.getenv(
            "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions"
        ).strip()

        self.ollama_url = os.getenv(
            "EDUCATION_OLLAMA_URL", "http://127.0.0.1:11434/api/generate"
        ).strip()
        self.ollama_model = os.getenv("EDUCATION_OLLAMA_MODEL", "llama3:latest").strip()
        self.enable_ollama = os.getenv(
            "EDUCATION_ENABLE_OLLAMA_FALLBACK", "true"
        ).strip().lower() in {"1", "true", "yes", "on"}

        if not (self.gemini_api_key or self.openrouter_api_key or self.enable_ollama):
            raise RuntimeError(
                "Configure EDUCATION_GEMINI_API_KEY, OPENROUTER_API_KEY, "
                "or enable Ollama fallback."
            )

    async def ainvoke(self, prompt: str) -> str:
        """Try providers in order; preserve ainvoke(prompt) for the router."""
        errors: list[str] = []

        if self.gemini_api_key:
            try:
                return await self._call_gemini(prompt)
            except Exception as exc:
                errors.append(f"Gemini: {type(exc).__name__}: {exc}")
                logger.warning("Education Gemini failed; trying OpenRouter/local fallback.")

        if self.openrouter_api_key:
            try:
                return await self._call_openrouter(prompt)
            except Exception as exc:
                errors.append(f"OpenRouter: {type(exc).__name__}: {exc}")
                logger.warning("Education OpenRouter failed; trying Ollama fallback.")

        if self.enable_ollama:
            try:
                return await self._call_ollama(prompt)
            except Exception as exc:
                errors.append(f"Ollama: {type(exc).__name__}: {exc}")
                logger.exception("Education Ollama fallback failed.")

        raise RuntimeError("All Education AI providers failed. " + " | ".join(errors))

    async def _call_gemini(self, prompt: str) -> str:
        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            f"{self.gemini_model}:generateContent"
        )
        payload: dict[str, Any] = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": float(os.getenv("EDUCATION_GEMINI_TEMPERATURE", "0.3")),
                "maxOutputTokens": int(os.getenv("EDUCATION_GEMINI_MAX_TOKENS", "16384")),
            },
        }
        transient_statuses = {429, 500, 502, 503, 504}
        attempts = max(1, int(os.getenv("EDUCATION_GEMINI_MAX_ATTEMPTS", "4")))

        async with httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout, connect=20.0)
        ) as client:
            for attempt in range(attempts):
                try:
                    response = await client.post(
                        url,
                        headers={"x-goog-api-key": self.gemini_api_key},
                        json=payload,
                    )
                except (httpx.TimeoutException, httpx.NetworkError) as exc:
                    if attempt == attempts - 1:
                        raise RuntimeError(
                            f"Gemini network failure after {attempts} attempts "
                            f"({type(exc).__name__}): {exc}"
                        ) from exc
                    wait = min(2 ** attempt, 20)
                    logger.warning("Gemini network error; retrying in %ss.", wait)
                    await asyncio.sleep(wait)
                    continue

                if response.status_code in transient_statuses:
                    if attempt == attempts - 1:
                        excerpt = response.text[:700].replace("\n", " ")
                        raise RuntimeError(
                            f"Gemini unavailable (HTTP {response.status_code}): {excerpt}"
                        )
                    try:
                        wait = float(response.headers.get("retry-after", ""))
                    except (TypeError, ValueError):
                        wait = 2 ** attempt
                    await asyncio.sleep(min(max(wait, 1.0), 20.0))
                    continue

                response.raise_for_status()
                data = response.json()
                candidates = data.get("candidates") or []
                if not candidates:
                    feedback = data.get("promptFeedback") or {}
                    reason = feedback.get("blockReason", "unknown reason")
                    raise RuntimeError(f"Gemini returned no candidates: {reason}")

                candidate = candidates[0]
                parts = (candidate.get("content") or {}).get("parts") or []
                text = "".join(
                    part.get("text", "")
                    for part in parts
                    if isinstance(part, dict) and isinstance(part.get("text"), str)
                ).strip()
                if not text:
                    raise RuntimeError(
                        "Gemini returned no text "
                        f"(finish reason: {candidate.get('finishReason', 'unknown')})."
                    )
                if candidate.get("finishReason") == "MAX_TOKENS":
                    raise RuntimeError(
                        "Gemini output was truncated by the token limit. Increase "
                        "EDUCATION_GEMINI_MAX_TOKENS or reduce the requested output."
                    )
                return text

        raise RuntimeError("Gemini failed after retries.")

    async def _call_openrouter(self, prompt: str) -> str:
        payload = {
            "model": self.openrouter_model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": float(os.getenv("EDUCATION_OPENROUTER_TEMPERATURE", "0.3")),
            "max_tokens": int(os.getenv("EDUCATION_OPENROUTER_MAX_TOKENS", "8192")),
        }
        headers = {
            "Authorization": f"Bearer {self.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", "http://localhost"),
            "X-Title": os.getenv("OPENROUTER_APP_NAME", "Education Assistant"),
        }
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(self.timeout, connect=20.0)
        ) as client:
            response = await client.post(
                self.openrouter_url, headers=headers, json=payload
            )
            response.raise_for_status()

        choices = response.json().get("choices") or []
        content = (choices[0].get("message") or {}).get("content") if choices else ""
        if isinstance(content, list):
            content = "".join(
                item.get("text", "") for item in content if isinstance(item, dict)
            )
        if not isinstance(content, str) or not content.strip():
            raise RuntimeError("OpenRouter returned an empty response.")
        return content.strip()

    async def _call_ollama(self, prompt: str) -> str:
        payload = {
            "model": self.ollama_model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": float(os.getenv("EDUCATION_OLLAMA_TEMPERATURE", "0.3")),
                "num_predict": int(os.getenv("EDUCATION_OLLAMA_NUM_PREDICT", "8192")),
            },
        }
        timeout = float(os.getenv("EDUCATION_OLLAMA_TIMEOUT_SECONDS", "300"))
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(timeout, connect=10.0)
        ) as client:
            response = await client.post(self.ollama_url, json=payload)
            response.raise_for_status()

        text = (response.json().get("response") or "").strip()
        if not text:
            raise RuntimeError("Ollama returned an empty response.")
        return text
