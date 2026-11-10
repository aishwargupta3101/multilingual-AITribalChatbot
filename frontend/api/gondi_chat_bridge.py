"""Gondi chat bridge using the existing English chat/RAG and local Hindi-Gondi MT."""
from __future__ import annotations

import re
from typing import Any

try:
    from api.gondi_translation import translate_gondi
except ModuleNotFoundError:
    from frontend.api.gondi_translation import translate_gondi


def _strip_markdown_for_translation(text: str) -> str:
    """Remove Markdown presentation before low-resource machine translation."""
    value = str(text or "").replace("\r\n", "\n").replace("\r", "\n").strip()
    value = re.sub(r"(?m)^\s*#{1,6}\s*", "", value)
    value = re.sub(r"(?m)^\s*(?:[-*+]\s+|\d+[.)]\s+)", "", value)
    value = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", value)
    value = re.sub(r"(\*\*|__)(.*?)\1", r"\2", value)
    value = re.sub(r"(?<!\*)\*(?!\*)(.*?)\*(?!\*)", r"\1", value)
    value = re.sub(r"(?<!_)_(?!_)(.*?)_(?!_)", r"\1", value)
    value = re.sub(r"`([^`]*)`", r"\1", value)
    value = re.sub(r"(?m)^[ \t]*[-*+][ \t]*$", "", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def _chat_call(prompt: str, session_id: str) -> Any:
    try:
        from api.client import APIClient
    except ModuleNotFoundError:
        from frontend.api.client import APIClient
    return APIClient.chat(question=prompt, session_id=session_id, language="english")


def _extract_answer(response: Any) -> tuple[str, dict[str, Any]]:
    if not isinstance(response, dict):
        raise ValueError("The English chat endpoint returned an invalid response.")
    if response.get("success") is False:
        raise RuntimeError(str(response.get("error") or response.get("message") or "English chat failed."))
    data = response.get("data")
    if not isinstance(data, dict):
        data = response
    answer = data.get("answer") or data.get("response") or data.get("message") or data.get("content")
    if isinstance(answer, dict):
        answer = answer.get("answer") or answer.get("content") or answer.get("message")
    if not isinstance(answer, str) or not answer.strip():
        raise ValueError("The English chat response did not contain an answer.")
    return answer.strip(), data


def ask_gondi_question(question: str, session_id: str, source_language: str = "english") -> dict[str, Any]:
    """Answer in Gondi; requires a locally fine-tuned Hindi-Gondi model."""
    text = str(question or "").strip()
    if not text:
        raise ValueError("Enter a question first.")
    source = str(source_language or "english").strip().lower().replace("-", "_").replace(" ", "_")
    if source in {"en", "eng", "english"}:
        source = "english"
        english_question = text
    elif source in {"gon", "gondi", "gondi_devanagari"}:
        source = "gondi"
        english_question = translate_gondi(text, "gondi_to_english")
    else:
        raise ValueError("Question language must be English or Gondi.")

    prompt = (
        "Answer the user's question in clear, simple English using Tribal AI's existing knowledge and RAG. "
        "The final answer will be machine-translated into Gondi. Use short declarative sentences, "
        "avoid Markdown headings and bullet lists, and do not invent facts.\n\n"
        f"Question: {english_question}"
    )
    english_response = _chat_call(prompt, session_id)
    english_answer, metadata = _extract_answer(english_response)
    plain_answer = _strip_markdown_for_translation(english_answer)
    gondi_answer = translate_gondi(plain_answer, "english_to_gondi")
    return {
        "answer": gondi_answer,
        "language": "gondi",
        "detected_language": source,
        "sources": metadata.get("sources", []),
        "images": metadata.get("images", []),
        "timestamp": metadata.get("timestamp", ""),
        "input_language": source,
        "output_language": "gondi",
        "translation_provider": "Local mT5 fine-tuned on Hindi-Gondi data via existing Hindi translation service",
    }
