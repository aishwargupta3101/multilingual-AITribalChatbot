"""Metadata catalog for India's 22 scheduled languages.

This is a registry, not a claim that every language has working translation,
speech recognition, or speech synthesis in this application. Capabilities stay
marked as planned until the corresponding implementation is integrated and tested.
"""
from copy import deepcopy
from typing import Any

# Language metadata follows the Eighth Schedule. Script labels are common usage,
# not a guarantee that every variety uses only one script.
_LANGUAGES: dict[str, dict[str, Any]] = {
    "assamese": {"display_name": "Assamese", "iso_639_3": "asm", "scripts": ["Assamese"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "bengali": {"display_name": "Bengali", "iso_639_3": "ben", "scripts": ["Bengali"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "bodo": {"display_name": "Bodo", "iso_639_3": "brx", "scripts": ["Devanagari"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "dogri": {"display_name": "Dogri", "iso_639_3": "doi", "scripts": ["Devanagari", "Perso-Arabic (varies)"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "gujarati": {"display_name": "Gujarati", "iso_639_3": "guj", "scripts": ["Gujarati"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "hindi": {"display_name": "Hindi", "iso_639_3": "hin", "scripts": ["Devanagari"], "capabilities": {"translation": "existing; verify end-to-end", "stt": "existing; verify end-to-end", "tts": "existing; verify end-to-end"}},
    "kannada": {"display_name": "Kannada", "iso_639_3": "kan", "scripts": ["Kannada"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "kashmiri": {"display_name": "Kashmiri", "iso_639_3": "kas", "scripts": ["Perso-Arabic", "Devanagari (varies)"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "konkani": {"display_name": "Konkani", "iso_639_3": "kok", "scripts": ["Devanagari", "other regional scripts"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "maithili": {"display_name": "Maithili", "iso_639_3": "mai", "scripts": ["Devanagari"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "malayalam": {"display_name": "Malayalam", "iso_639_3": "mal", "scripts": ["Malayalam"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "manipuri": {"display_name": "Manipuri (Meitei)", "iso_639_3": "mni", "scripts": ["Bengali", "Meitei Mayek"], "capabilities": {"translation": "existing; verify end-to-end", "stt": "existing; verify end-to-end", "tts": "existing; verify end-to-end"}},
    "marathi": {"display_name": "Marathi", "iso_639_3": "mar", "scripts": ["Devanagari"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "nepali": {"display_name": "Nepali", "iso_639_3": "nep", "scripts": ["Devanagari"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "odia": {"display_name": "Odia", "iso_639_3": "ori", "scripts": ["Odia"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "punjabi": {"display_name": "Punjabi", "iso_639_3": "pan", "scripts": ["Gurmukhi", "Shahmukhi (regional)"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "sanskrit": {"display_name": "Sanskrit", "iso_639_3": "san", "scripts": ["Devanagari", "other scripts"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "santali": {"display_name": "Santali", "iso_639_3": "sat", "scripts": ["Ol Chiki", "Devanagari/Bengali/Odia (regional use)"], "capabilities": {"translation": "existing candidate; verify model pairs", "stt": "existing candidate; verify model and script", "tts": "requires validated voice/model"}},
    "sindhi": {"display_name": "Sindhi", "iso_639_3": "snd", "scripts": ["Perso-Arabic", "Devanagari (regional use)"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "tamil": {"display_name": "Tamil", "iso_639_3": "tam", "scripts": ["Tamil"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "telugu": {"display_name": "Telugu", "iso_639_3": "tel", "scripts": ["Telugu"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
    "urdu": {"display_name": "Urdu", "iso_639_3": "urd", "scripts": ["Perso-Arabic"], "capabilities": {"translation": "planned", "stt": "planned", "tts": "planned"}},
}

# Existing tribal/regional languages are kept in the same catalog so the UI/API
# can expose them without implying that they are Eighth Schedule languages.
_TRIBAL_LANGUAGES: dict[str, dict[str, Any]] = {
    "gondi": {"display_name": "Gondi", "iso_639_3": "gon", "scripts": ["Devanagari", "Telugu", "regional scripts"], "category": "tribal/regional", "capabilities": {"translation": "candidate; validate dialect and data", "stt": "candidate; validate dialect/model", "tts": "candidate; validate dialect/model"}},
    "tai_khamti": {"display_name": "Tai Khamti", "iso_639_3": "kht", "scripts": ["Tai Tham/other local conventions"], "category": "tribal/regional", "capabilities": {"translation": "existing RAG; translation needs validation", "stt": "needs validation", "tts": "needs validation"}},
    "monpa": {"display_name": "Monpa", "iso_639_3": None, "scripts": ["varies by variety"], "category": "tribal/regional", "capabilities": {"translation": "needs variety and model validation", "stt": "needs variety and model validation", "tts": "needs variety and model validation"}},
    "naga": {"display_name": "Naga languages", "iso_639_3": None, "scripts": ["Latin and local conventions"], "category": "tribal/regional umbrella; select language variety", "capabilities": {"translation": "select language first", "stt": "select language first", "tts": "select language first"}},
    "mishmi": {"display_name": "Mishmi languages", "iso_639_3": None, "scripts": ["varies by language/variety"], "category": "tribal/regional umbrella; select language variety", "capabilities": {"translation": "select language first", "stt": "select language first", "tts": "select language first"}},
}


def list_languages(include_tribal: bool = True) -> list[dict[str, Any]]:
    """Return copied metadata, sorted by stable key."""
    catalog = dict(_LANGUAGES)
    if include_tribal:
        catalog.update(_TRIBAL_LANGUAGES)
    return [{"key": key, **deepcopy(catalog[key])} for key in sorted(catalog)]


def get_language(language_key: str) -> dict[str, Any]:
    """Return copied metadata for a language key or raise ValueError."""
    if not isinstance(language_key, str) or not language_key.strip():
        raise ValueError("language_key must be a non-empty string")
    key = language_key.strip().lower().replace("-", "_").replace(" ", "_")
    item = _LANGUAGES.get(key) or _TRIBAL_LANGUAGES.get(key)
    if item is None:
        raise ValueError(f"Unknown language: {language_key}")
    return deepcopy({"key": key, **item})


def scheduled_language_keys() -> list[str]:
    """Return keys for the 22 Eighth Schedule languages only."""
    return sorted(_LANGUAGES)
