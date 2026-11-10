"""Safe translation adapter for experimental tribal-language support.

This module intentionally does not assume NLLB supports Gondi, Santali, or any
Monpa variety. A language pair must be explicitly verified and a translator
backend supplied before translation is enabled.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

from .language_registry import get_language


class TranslationConfigurationError(ValueError):
    """Raised when translation configuration is missing or invalid."""


class TranslationNotReadyError(RuntimeError):
    """Raised when a language pair has not been validated for translation."""


class TranslationExecutionError(RuntimeError):
    """Raised when a configured translation backend fails or returns no text."""


@dataclass(frozen=True)
class TranslationResult:
    text: str
    source_language: str
    target_language: str
    backend_name: str


Translator = Callable[[str, str, str], str]


class TribalTranslationService:
    """Dispatch translation only for explicitly verified language pairs.

    Args:
        translator: Callable with signature ``translator(text, source, target)``.
            It can wrap a compatible model/service already used by the project.
        verified_pairs: Iterable of (source, target) pairs verified by testing.
            Example: ``[("santali", "english")]``. No pairs are enabled by
            default. Include reverse directions separately if tested.
        backend_name: Human-readable name for result metadata.
        max_input_chars: Guard against unexpectedly large requests.

    This class does not download/load a model itself. That avoids loading a
    potentially incompatible checkpoint or silently routing unsupported pairs
    into the existing Manipuri translation service.
    """

    SUPPORTED_TRIBAL_LANGUAGES = {"gondi", "santali", "monpa"}
    COMMON_LANGUAGE_ALIASES = {
        "en": "english", "eng": "english",
        "hi": "hindi", "hin": "hindi",
        "gond": "gondi", "sat": "santali",
    }

    def __init__(
        self,
        translator: Translator | None = None,
        verified_pairs: Iterable[tuple[str, str]] = (),
        backend_name: str = "unconfigured",
        max_input_chars: int = 10_000,
    ) -> None:
        self.translator = translator
        self.backend_name = str(backend_name or "unconfigured").strip()
        self.max_input_chars = int(max_input_chars)
        if self.max_input_chars < 1:
            raise TranslationConfigurationError("max_input_chars must be positive")
        self.verified_pairs = {
            (self.normalize_language(src), self.normalize_language(dst))
            for src, dst in verified_pairs
        }
        for src, dst in self.verified_pairs:
            if not src or not dst:
                raise TranslationConfigurationError("Language-pair values cannot be empty")

    @classmethod
    def normalize_language(cls, language: str) -> str:
        value = str(language or "").strip().lower().replace("-", "_").replace(" ", "_")
        return cls.COMMON_LANGUAGE_ALIASES.get(value, value)

    @staticmethod
    def _validate_language(language: str) -> str:
        if not language:
            raise TranslationConfigurationError("Both source and target languages are required")
        # The experimental service only accepts the three languages this lab owns
        # plus common pivot languages. Existing project translation stays separate.
        known = {"gondi", "santali", "monpa", "english", "hindi"}
        if language not in known:
            raise TranslationConfigurationError(
                f"Language '{language}' is outside this experimental translation service"
            )
        if language == "monpa":
            # A variety must be explicitly selected/validated before model routing.
            raise TranslationNotReadyError(
                "Monpa translation requires a selected and validated variety "
                "(for example, Tawang Monpa or Kalaktang Monpa)."
            )
        return language

    def supported_pairs(self) -> list[dict[str, str]]:
        """List only explicitly enabled pairs; this is not a claim of model coverage."""
        return [
            {"source_language": src, "target_language": dst}
            for src, dst in sorted(self.verified_pairs)
        ]

    def translate(self, text: str, source_language: str, target_language: str) -> TranslationResult:
        if not isinstance(text, str):
            raise TypeError("text must be a string")
        text = text.strip()
        if not text:
            return TranslationResult(
                text="",
                source_language=self.normalize_language(source_language),
                target_language=self.normalize_language(target_language),
                backend_name=self.backend_name,
            )
        if len(text) > self.max_input_chars:
            raise ValueError(f"Input exceeds the {self.max_input_chars}-character limit")

        source = self._validate_language(self.normalize_language(source_language))
        target = self._validate_language(self.normalize_language(target_language))
        if source == target:
            return TranslationResult(text, source, target, "identity")

        if (source, target) not in self.verified_pairs:
            raise TranslationNotReadyError(
                f"Translation pair '{source} -> {target}' has not been verified and enabled. "
                "Check model language-token support and evaluate the pair before enabling it."
            )
        if self.translator is None:
            raise TranslationConfigurationError(
                "A translation backend is not configured. Supply a tested translator callable."
            )

        try:
            translated = self.translator(text, source, target)
        except Exception as exc:
            raise TranslationExecutionError(
                f"Translation backend failed for '{source} -> {target}'."
            ) from exc
        if not isinstance(translated, str) or not translated.strip():
            raise TranslationExecutionError(
                f"Translation backend returned empty output for '{source} -> {target}'."
            )
        return TranslationResult(
            text=translated.strip(),
            source_language=source,
            target_language=target,
            backend_name=self.backend_name,
        )
