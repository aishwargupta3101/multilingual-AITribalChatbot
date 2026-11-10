"""Central language capability registry for optional Indic voice support.

Only languages listed here are exposed through the generic Whisper/gTTS route.
This does not replace dedicated Manipuri or Santali implementations.
Set ENABLE_EXPERIMENTAL_INDIC_VOICE=1 to enable the additional generic Indic routes.
"""
import os
_INDIC_STT = {
    "assamese": "as",
    "bengali": "bn",
    "gujarati": "gu",
    "kannada": "kn",
    "malayalam": "ml",
    "marathi": "mr",
    "nepali": "ne",
    "punjabi": "pa",
    "sanskrit": "sa",
    "tamil": "ta",
    "telugu": "te",
    "urdu": "ur",
}

# gTTS codes are provider-backed and can vary with the installed gTTS version.
_INDIC_TTS_CANDIDATES = {
    "assamese": "as",
    "bengali": "bn",
    "gujarati": "gu",
    "kannada": "kn",
    "malayalam": "ml",
    "marathi": "mr",
    "nepali": "ne",
    "punjabi": "pa",
    "tamil": "ta",
    "telugu": "te",
    "urdu": "ur",
}

def _enabled() -> bool:
    return os.getenv("ENABLE_EXPERIMENTAL_INDIC_VOICE", "0").strip().lower() in {"1", "true", "yes", "on"}

def stt_language_map() -> dict[str, str]:
    return dict(_INDIC_STT) if _enabled() else {}

def stt_languages() -> set[str]:
    base = {"english", "hindi", "manipuri", "manipuri_mtei"}
    return base | set(stt_language_map())

def tts_language_map() -> dict[str, str]:
    if not _enabled():
        return {}
    try:
        from gtts.lang import tts_langs
        available = tts_langs()
        return {name: code for name, code in _INDIC_TTS_CANDIDATES.items() if code in available.values()}
    except Exception:
        return {}
