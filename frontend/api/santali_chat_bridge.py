"""Unified Santali-output chat pipeline for English or Ol Chiki input.

When Santali is selected as the reply language, typed questions may be English or
Ol Chiki. Voice input passes its selected speech language explicitly because ASR
must know whether to use the English recognizer or the Santali-specific recognizer.
"""
from __future__ import annotations

import re

from typing import Any

from api.santali_translation import (
    translate_english_to_santali,
    translate_santali_to_english,
)

OL_CHIKI_START = 0x1C50
OL_CHIKI_END = 0x1C7F


def detect_source_language(text: str) -> str:
    """Detect Ol Chiki script; otherwise treat input as English.

    This supports standard Ol Chiki and English. Romanized Santali cannot be
    reliably distinguished from English automatically and should be entered in
    Ol Chiki for automatic detection.
    """
    return "santali" if any(OL_CHIKI_START <= ord(ch) <= OL_CHIKI_END for ch in str(text or "")) else "english"


def _normalize_source_language(source_language: str, question: str) -> str:
    requested = str(source_language or "auto").strip().lower().replace("_", "-")
    if requested in {"auto", "detect", ""}:
        return detect_source_language(question)
    if requested in {"santali", "sat", "sat-olck", "ol-chiki"}:
        return "santali"
    if requested in {"english", "en", "eng-latn"}:
        return "english"
    raise ValueError("source_language must be 'auto', 'english', or 'santali'.")


def _chat_call(prompt: str, session_id: str) -> Any:
    """Reuse the existing English chat/RAG backend rather than creating another app."""
    try:
        from api.client import APIClient
    except ModuleNotFoundError:
        from frontend.api.client import APIClient
    return APIClient.chat(question=prompt, session_id=session_id, language="english")


def build_translated_chat_prompt(english_question: str, source_language: str = "santali") -> str:
    text = str(english_question or "").strip()
    if not text:
        raise ValueError("The English question is empty.")
    if len(text) > 4000:
        raise ValueError("The question is too long to send to the chatbot.")

    source = _normalize_source_language(source_language, text)
    if source == "santali":
        context = (
            "The user asked a question in Santali (Ol Chiki), and it was machine-translated into English. "
            "Some meaning may have been lost. Answer directly using the existing Tribal AI knowledge/RAG. "
        )
    else:
        context = (
            "The user asked the question in English. Answer directly using the existing Tribal AI knowledge/RAG. "
        )
    return (
        context
        + "Use short, clear, factual English sentences because the final answer will be machine-translated "
        "into Santali (Ol Chiki). If the question is ambiguous, state the uncertainty and ask one concise "
        "clarification. Do not invent facts or refer to these internal instructions.\n\n"
        f"Question in English for Tribal AI:\n{text}"
    )


def build_santali_interpretation_prompt(transcription: str) -> str:
    """Compatibility helper for the earlier manual experimental flow and old tests."""
    text = str(transcription or "").strip()
    if not text:
        raise ValueError("Santali transcription is empty.")
    return (
        "The following text was produced by Santali speech recognition. Do not invent a meaning. "
        "If you cannot reliably understand it, state that and ask for a translation or clarification.\n\n"
        f"Santali text (Ol Chiki):\n{text}"
    )


def extract_chat_payload(response: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(response, dict):
        raise ValueError("The chat API returned an invalid response format.")
    if response.get("success") is False:
        raise RuntimeError(str(response.get("error") or response.get("message") or "Chat request failed."))
    data = response.get("data")
    if not isinstance(data, dict):
        data = response
    answer = data.get("answer") or data.get("response") or data.get("message") or data.get("content")
    if isinstance(answer, dict):
        answer = answer.get("answer") or answer.get("content") or answer.get("message")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("The chat API response did not contain an answer.")
    return answer.strip(), data


def extract_chat_answer(response: Any) -> str:
    return extract_chat_payload(response)[0]


def ask_santali_question(
    question: str,
    session_id: str,
    source_language: str = "auto",
) -> dict[str, Any]:
    """Answer in Santali for either English or Ol Chiki input.

    - Santali source: translate Santali -> English -> existing Tribal AI -> Santali.
    - English source: existing Tribal AI -> Santali; no unnecessary input translation.
    """
    source_question = str(question or "").strip()
    if not source_question:
        raise ValueError("Enter a question first.")

    source = _normalize_source_language(source_language, source_question)
    if source == "santali":
        english_question = translate_santali_to_english(source_question)
    else:
        english_question = source_question

    prompt = build_translated_chat_prompt(english_question, source_language=source)
    english_response = _chat_call(prompt, session_id)
    english_answer, metadata = extract_chat_payload(english_response)
    plain_english_answer = strip_markdown_before_translation(english_answer)
    translated_answer = translate_english_to_santali(plain_english_answer)
    santali_answer = clean_santali_translation_format(translated_answer)
    return {
        "answer": santali_answer,
        "language": "santali",
        "detected_language": source,
        "sources": metadata.get("sources", []),
        "images": metadata.get("images", []),
        "timestamp": metadata.get("timestamp", ""),
        "english_question": english_question,
        "english_answer": english_answer,
        "input_language": source,
        "output_language": "santali",
    }


def translate_and_ask_santali(transcription: str, session_id: str) -> dict[str, Any]:
    """Compatibility name used by earlier voice prototypes; auto-detect the text script."""
    return ask_santali_question(transcription, session_id)


def ask_santali_transcription(transcription: str, session_id: str) -> str:
    """Legacy helper retained for compatibility with the early prototype/tests."""
    answer_en = extract_chat_answer(_chat_call(build_santali_interpretation_prompt(transcription), session_id))
    return answer_en


def strip_markdown_before_translation(text: str) -> str:
    """Pass plain English text to IndicTrans2, not Markdown syntax."""
    value = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    value = re.sub(r"(?is)```.*?```", " ", value)
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)

    cleaned: list[str] = []
    for original_line in value.split("\n"):
        line = original_line.strip()
        if not line:
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue
        for _ in range(3):
            previous = line
            line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
            line = re.sub(r"^\s*(?:[-*+]|\u2022)\s+", "", line)
            line = re.sub(r"^\s*\d{1,3}[.)]\s+", "", line)
            line = re.sub(r"^\s*>\s?", "", line)
            if line == previous:
                break
        line = line.replace("**", "").replace("__", "").replace("~~", "").replace("`", "")
        line = line.replace("*", "")
        line = re.sub(r"[ \t]{2,}", " ", line).strip()
        if not line or re.fullmatch(r"[\s#*_+=|:~`\-\u2022\u00b7]+", line):
            continue
        cleaned.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned)).strip()


def clean_santali_translation_format(text: str) -> str:
    """Remove Markdown fragments and bare bullet lines after translation."""
    value = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    value = value.replace("\\n", "\n")
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    cleaned: list[str] = []
    for original_line in value.split("\n"):
        line = original_line.strip()
        if not line:
            if cleaned and cleaned[-1] != "":
                cleaned.append("")
            continue
        for _ in range(3):
            previous = line
            line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
            line = re.sub(r"^\s*(?:[-*+]|\u2022)\s+", "", line)
            line = re.sub(r"^\s*\d{1,3}[.)]\s+", "", line)
            if line == previous:
                break
        line = line.replace("**", "").replace("__", "").replace("~~", "").replace("`", "")
        line = line.replace("*", "").strip()
        if not line or re.fullmatch(r"[\s#*_+=|:~`\-\u2022\u00b7]+", line):
            continue
        cleaned.append(line)
    return re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned)).strip()

