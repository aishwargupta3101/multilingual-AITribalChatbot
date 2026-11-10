"""
Tribal AI response cleanup helper.

Purpose:
- Remove accidental trailing code blocks containing only HTML closing tags
  (for example: ```html </div> </div> ```).
- Remove standalone raw closing-tag lines accidentally appended to normal answers.
- Avoid changing font, CSS, Markdown rendering, translations, or valid source code.

This module is additive. It only takes effect after the backend calls
clean_assistant_response() immediately before returning the final assistant text.
"""
from __future__ import annotations

import re
from typing import Any


_HTML_TAG_ONLY = re.compile(
    r"^\s*</?(?:div|span|p|section|article|main|header|footer|pre|code|"
    r"strong|em|ul|ol|li|table|thead|tbody|tr|td|th|br|hr)(?:\s+[^<>]*)?\s*/?>\s*$",
    re.IGNORECASE,
)
_FENCE_LINE = re.compile(r"^\s*(```+|~~~+)(.*)$")


def _is_html_artifact_block(block: str) -> bool:
    """True only when a fenced block contains nothing except HTML tag lines."""
    lines = block.strip().splitlines()
    if not lines:
        return True

    # Allow a first language marker such as ```html, but require every remaining
    # nonblank line to be an HTML tag. Do not delete legitimate code blocks.
    if lines and re.fullmatch(r"(?:html|xml|markup)", lines[0].strip(), re.IGNORECASE):
        lines = lines[1:]

    nonblank = [line.strip() for line in lines if line.strip()]
    return bool(nonblank) and all(_HTML_TAG_ONLY.fullmatch(line) for line in nonblank)


def clean_assistant_response(value: Any) -> str:
    """
    Convert a plain assistant response to text and remove known HTML artifacts.

    Structured list/dict values are not stringified as '[object Object]'; they
    are rejected to an empty string so callers can log and inspect the payload
    shape rather than showing implementation objects to the user.
    """
    if value is None:
        return ""
    if not isinstance(value, str):
        # The chat layer should extract the actual content field before calling
        # this function. Avoid displaying a raw object representation.
        return ""

    text = value.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    # Remove standalone raw HTML tag lines outside fenced code. Track fences so
    # that code examples containing HTML remain intact.
    output: list[str] = []
    fence_char: str | None = None
    fence_len = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        fence_match = _FENCE_LINE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if fence_char is None:
                fence_char = marker[0]
                fence_len = len(marker)
                # Capture this fenced block as a unit.
                j = i + 1
                closing = None
                while j < len(lines):
                    close_match = _FENCE_LINE.match(lines[j])
                    if close_match and close_match.group(1)[0] == fence_char and len(close_match.group(1)) >= fence_len:
                        closing = j
                        break
                    j += 1

                if closing is not None:
                    body = "\n".join(lines[i + 1:closing])
                    info = fence_match.group(2).strip()
                    if _is_html_artifact_block((info + "\n" if info else "") + body):
                        i = closing + 1
                        continue
                    output.extend(lines[i:closing + 1])
                    i = closing + 1
                    fence_char = None
                    fence_len = 0
                    continue

                # Unclosed fence: preserve it verbatim rather than risk deleting code.
                output.extend(lines[i:])
                break
            else:
                # This branch is defensive; normal blocks are consumed above.
                fence_char = None
                fence_len = 0
                output.append(line)
                i += 1
                continue

        if fence_char is None and _HTML_TAG_ONLY.fullmatch(line.strip()):
            i += 1
            continue

        output.append(line)
        i += 1

    cleaned = "\n".join(output)
    # Remove excessive trailing blank lines left by artifact removal.
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned).rstrip()
    return cleaned


def clean_response_payload(payload: Any) -> str:
    """Extract plain text from common LLM response shapes, then clean it."""
    if isinstance(payload, str) or payload is None:
        return clean_assistant_response(payload)
    if isinstance(payload, dict):
        for key in ("content", "text", "answer", "response", "output"):
            value = payload.get(key)
            if isinstance(value, str):
                return clean_assistant_response(value)
    # Support common message objects that expose a string .content attribute.
    content = getattr(payload, "content", None)
    if isinstance(content, str):
        return clean_assistant_response(content)
    return ""
