"""Additive TTS interface for experimental tribal-language support.

This module intentionally does not load a model by itself. Connect a verified,
language-compatible backend through the injected ``backend`` callable. This
keeps existing TTS services unchanged and avoids claiming unsupported language
coverage.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional, Any


class TribalTTSConfigurationError(ValueError):
    """Raised when the requested language or backend configuration is invalid."""


class TribalTTSUnavailableError(RuntimeError):
    """Raised when a verified TTS backend is not configured for a language."""


class TribalTTSGenerationError(RuntimeError):
    """Raised when the configured backend fails to generate audio."""


@dataclass(frozen=True)
class TTSResult:
    language: str
    audio: Any
    content_type: str = "audio/wav"


# Only languages that have been explicitly connected to a verified backend
# should be placed in this set. Empty by default by design.
DEFAULT_ENABLED_LANGUAGES: frozenset[str] = frozenset()


class TribalTTSService:
    """Validate requests and delegate synthesis to an injected TTS backend.

    ``backend`` must accept keyword arguments ``text`` and ``language`` and
    return non-empty audio bytes (or another documented audio payload).
    """

    def __init__(
        self,
        backend: Optional[Callable[..., Any]] = None,
        enabled_languages: Optional[set[str] | frozenset[str]] = None,
        content_type: str = "audio/wav",
    ) -> None:
        self.backend = backend
        self.enabled_languages = frozenset(
            language.strip().lower()
            for language in (
                DEFAULT_ENABLED_LANGUAGES
                if enabled_languages is None
                else enabled_languages
            )
        )
        self.content_type = content_type

    def synthesize(self, text: str, language: str) -> TTSResult:
        if not isinstance(text, str) or not text.strip():
            raise TribalTTSConfigurationError("Text must be a non-empty string.")
        if not isinstance(language, str) or not language.strip():
            raise TribalTTSConfigurationError("Language must be a non-empty string.")

        language_key = language.strip().lower()
        if language_key not in {"gondi", "santali", "monpa"}:
            raise TribalTTSConfigurationError(
                f"Unsupported experimental language: {language_key}"
            )

        if language_key not in self.enabled_languages:
            raise TribalTTSUnavailableError(
                f"TTS is not enabled for {language_key}; verify and configure a "
                "compatible language-specific model first."
            )

        if self.backend is None:
            raise TribalTTSUnavailableError(
                f"No TTS backend is configured for {language_key}."
            )

        try:
            audio = self.backend(text=text.strip(), language=language_key)
        except Exception as exc:
            raise TribalTTSGenerationError(
                f"TTS generation failed for {language_key}."
            ) from exc

        if audio is None or audio == b"" or audio == "":
            raise TribalTTSGenerationError(
                f"TTS backend returned empty audio for {language_key}."
            )

        return TTSResult(
            language=language_key,
            audio=audio,
            content_type=self.content_type,
        )
