"""Registry for planned tribal-language capabilities.

This registry intentionally distinguishes a candidate model from a verified
capability. Do not mark a capability as ready until the model, language variety,
licence, and evaluation data have been checked.
"""

from copy import deepcopy
from typing import Any


_LANGUAGE_REGISTRY: dict[str, dict[str, Any]] = {
    "gondi": {
        "display_name": "Gondi",
        "variety": "unspecified",
        "language_codes": {"iso_639_3": "gon"},
        "capabilities": {
            "stt": {
                "status": "candidate",
                "model_id": "facebook/mms-1b-all",
                "notes": "Verify that the required Gondi variety has a usable MMS adapter and test real recordings.",
            },
            "translation": {
                "status": "needs_validation",
                "model_id": None,
                "notes": "Validate each direction with a human-reviewed Gondi-Hindi/English parallel set.",
            },
            "tts": {
                "status": "candidate",
                "model_id": "facebook/mms-tts-wsg",
                "notes": "Candidate is associated with Adilabad Gondi; confirm dialect fit, repository availability, and licence before use.",
            },
        },
    },
    "santali": {
        "display_name": "Santali",
        "variety": "specify script/variety for the dataset",
        "language_codes": {"iso_639_3": "sat"},
        "capabilities": {
            "stt": {
                "status": "candidate",
                "model_id": "facebook/mms-1b-all",
                "notes": "Verify the Santali adapter and script conventions; evaluate against human transcripts.",
            },
            "translation": {
                "status": "needs_validation",
                "model_id": "facebook/nllb-200-distilled-600M",
                "notes": "Confirm the exact source/target language tokens before attempting direct translation.",
            },
            "tts": {
                "status": "needs_model_search",
                "model_id": None,
                "notes": "Do not enable TTS until a compatible checkpoint or custom model is validated.",
            },
        },
    },
    "monpa": {
        "display_name": "Monpa",
        "variety": "must_select",
        "language_codes": {
            "tawang_monpa": "twm",
            "kalaktang_monpa": "kkf",
            "ala_tshangla": "tbo",
        },
        "capabilities": {
            "stt": {
                "status": "needs_validation",
                "model_id": "facebook/mms-1b-all",
                "notes": "Do not infer support from MMS being multilingual; verify a usable adapter for the selected variety.",
            },
            "translation": {
                "status": "needs_data_and_validation",
                "model_id": "facebook/nllb-200-distilled-600M",
                "notes": "Verify language-token support; otherwise use a reviewed corpus and a separately validated approach.",
            },
            "tts": {
                "status": "needs_data_or_model_search",
                "model_id": None,
                "notes": "Requires a validated voice checkpoint or a custom voice-training dataset.",
            },
        },
    },
}


def list_languages() -> list[dict[str, Any]]:
    """Return all configured languages without exposing mutable internals."""
    return [
        {"key": key, **deepcopy(value)}
        for key, value in _LANGUAGE_REGISTRY.items()
    ]


def get_language(language_key: str) -> dict[str, Any]:
    """Return configuration for a language key or raise ValueError."""
    key = language_key.strip().lower().replace(" ", "_")
    try:
        return deepcopy(_LANGUAGE_REGISTRY[key])
    except KeyError as exc:
        available = ", ".join(_LANGUAGE_REGISTRY)
        raise ValueError(
            f"Unknown tribal language '{language_key}'. Available: {available}"
        ) from exc


def get_capability(language_key: str, capability: str) -> dict[str, Any]:
    """Return a capability record; capability must be stt, translation, or tts."""
    capability_key = capability.strip().lower()
    if capability_key not in {"stt", "translation", "tts"}:
        raise ValueError("capability must be one of: stt, translation, tts")
    language = get_language(language_key)
    return language["capabilities"][capability_key]


def capability_is_ready(language_key: str, capability: str) -> bool:
    """Only explicit 'ready' status enables a capability in production."""
    return get_capability(language_key, capability).get("status") == "ready"
