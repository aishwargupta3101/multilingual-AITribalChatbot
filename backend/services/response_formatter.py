"""
Language-agnostic formatting helpers for Tribal AI responses.
Presentation only: does not translate, summarize, or intentionally remove content.
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

def _split_flat_paragraphs(text: str) -> str:
    """Add paragraph breaks to long flattened prose, leaving Markdown structures alone."""
    output = []
    in_fence = False
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith(("```", "~~~")):
            in_fence = not in_fence
            output.append(line)
            continue
        structural = (
            not stripped or in_fence
            or re.match(r"^#{1,6}\s", stripped)
            or re.match(r"^(?:[-*+]|\d+[.)])\s+", stripped)
            or stripped.startswith((">", "|"))
        )
        if structural:
            output.append(line.rstrip())
            continue
        # Only split a flattened line if it is long enough to benefit from paragraphs.
        if len(stripped) >= 320:
            sentences = re.split(r"(?<=[.!?।॥。！？])\s+", stripped)
            if len(sentences) >= 4:
                for i in range(0, len(sentences), 2):
                    paragraph = " ".join(part.strip() for part in sentences[i:i + 2] if part.strip())
                    if paragraph:
                        output.append(paragraph)
                        if i + 2 < len(sentences):
                            output.append("")
                continue
        output.append(line.rstrip())
    return "\n".join(output)

def format_response(text: str, language: Optional[str] = None) -> str:
    """Normalize layout for English, Hindi, Manipuri, Tai Khamti, and other languages."""
    if text is None:
        return ""
    if not isinstance(text, str):
        text = str(text)
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\u2028", "\n").replace("\ufeff", "").replace("\u200b", "")
    text = text.replace("\u00a0", " ")
    text = _repair_heading_spacing(text)
    text = _split_flat_paragraphs(text)
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
