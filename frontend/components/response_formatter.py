"""
Language-agnostic response formatting helpers for Tribal AI Chatbot.
Presentation-only: does not translate, summarize, or intentionally remove content.
"""
import re
from typing import Optional

SUPPORTED_LANGUAGE_ALIASES = {
    "en": "english", "eng": "english", "hi": "hindi", "hin": "hindi",
    "mni": "manipuri", "mni_beng": "manipuri", "manipuri_beng": "manipuri",
    "manipuri_bengali": "manipuri", "meitei": "manipuri",
    "mni_mtei": "manipuri_mtei", "meitei_mayek": "manipuri_mtei",
    "manipuri_meitei": "manipuri_mtei", "tai_khamti": "tai_khamti",
}

def normalize_language(language: Optional[str]) -> str:
    value = str(language or "").strip().lower().replace("-", "_").replace(" ", "_")
    return SUPPORTED_LANGUAGE_ALIASES.get(value, value)

def _repair_heading_spacing(text: str) -> str:
    lines, output, in_fence = text.split("\n"), [], False
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            output.append(line)
            continue
        if not in_fence:
            match = re.match(r"^(\s{0,3}#{1,6})(\S.*)$", line)
            if match:
                line = f"{match.group(1)} {match.group(2)}"
        output.append(line)
    return "\n".join(output)

def format_response(text: str, language: Optional[str] = None) -> str:
    """Normalize Markdown layout for English, Hindi, Manipuri, Tai Khamti, and other languages."""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u2028", "\n").replace("\ufeff", "").replace("\u200b", "")
    text = text.replace("\u00a0", " ")
    text = _repair_heading_spacing(text)
    lines, output, in_fence = text.split("\n"), [], False
    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            output.append(line.rstrip())
            continue
        if not in_fence:
            # Put headings, bullets and numbered items on their own lines
            # when a model/translation has flattened Markdown into a paragraph.
            line = re.sub(r"\s+(?=#{1,6}\s)", "\n\n", line)
            line = re.sub(r"(?<=[.!?。！？])\s+(?=(?:[-*+]|\d+[.)])\s+)", "\n", line)
        output.append(line.rstrip())
    text = "\n".join(output)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

def format_for_display(text: str, language: Optional[str] = None) -> str:
    return format_response(text, language)

def format_for_voice(text: str, language: Optional[str] = None) -> str:
    """Return plain text for TTS while preserving words and paragraph breaks."""
    formatted = format_response(text, language)
    if not formatted:
        return ""
    output, in_fence = [], False
    for line in formatted.split("\n"):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            continue
        if not in_fence:
            line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
            line = re.sub(r"^\s*(?:[-*+]|\d+[.)])\s+", "", line)
            line = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", line)
            line = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", line)
            line = re.sub(r"(\*\*|__)(.*?)\1", r"\2", line)
            line = re.sub(r"(?<!\*)\*(?!\*)(.*?)\*(?!\*)", r"\1", line)
            line = re.sub(r"(?<!_)_(?!_)(.*?)_(?!_)", r"\1", line)
            line = re.sub(r"`([^`]*)`", r"\1", line)
        output.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(output)).strip()

if __name__ == "__main__":
    examples = [
        ("english", "##Artificial Intelligence\n\nAI is **useful**.\n- Example one"),
        ("hindi", "##कृत्रिम बुद्धिमत्ता\n\nAI उपयोगी है।\n- पहला उदाहरण"),
        ("manipuri", "##ꯃꯤꯇꯩ\n\nꯃꯁꯤ **ꯐꯖꯩ**।"),
        ("manipuri_mtei", "##ꯃꯤꯇꯩ\n\nꯃꯁꯤ ꯐꯖꯩ।"),
        ("tai_khamti", "##Example\n\nA paragraph.\n1. First item"),
    ]
    for language, sample in examples:
        print(f"--- {language} ---")
        print(format_response(sample, language))
        print("[TTS]", format_for_voice(sample, language))
