from __future__ import annotations

import ast
import re
import shutil
from datetime import datetime
from pathlib import Path


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

        # Remove structural Markdown prefixes but preserve the text of each item.
        # Loop so malformed combinations like "* ###Title" are fully stripped.
        for _ in range(3):
            previous = line
            line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
            line = re.sub(r"^\s*(?:[-*+]|\u2022)\s+", "", line)
            line = re.sub(r"^\s*\d{1,3}[.)]\s+", "", line)
            line = re.sub(r"^\s*>\s?", "", line)
            if line == previous:
                break

        # Remove inline emphasis/code delimiters, not the words they surround.
        line = line.replace("**", "").replace("__", "").replace("~~", "").replace("`", "")
        line = line.replace("*", "")
        line = re.sub(r"[ \t]{2,}", " ", line).strip()

        # Skip lines that contain only Markdown separators or list markers.
        if not line or re.fullmatch(r"[\s#*_+=|:~`\-\u2022\u00b7]+", line):
            continue
        cleaned.append(line)

    return re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned)).strip()


def clean_santali_translation_format(text: str) -> str:
    """Remove Markdown fragments/bare bullet lines left by translating formatted text."""
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

        # Repeat a few times because translation may leave nested markers such as '* ###Title'.
        for _ in range(3):
            previous = line
            line = re.sub(r"^\s{0,3}#{1,6}\s*", "", line)
            line = re.sub(r"^\s*(?:[-*+]|\u2022)\s+", "", line)
            line = re.sub(r"^\s*\d{1,3}[.)]\s+", "", line)
            if line == previous:
                break

        line = line.replace("**", "").replace("__", "").replace("~~", "").replace("`", "")
        # Asterisks and underscores often appear as orphaned markup after translation.
        line = line.replace("*", "").replace("__", "").strip()
        if not line or re.fullmatch(r"[\s#*_+=|:~`\-\u2022\u00b7]+", line):
            continue
        cleaned.append(line)

    result = re.sub(r"\n{3,}", "\n\n", "\n".join(cleaned)).strip()
    return result


def main() -> int:
    root = Path(__file__).resolve().parent
    target = root / "frontend" / "api" / "santali_chat_bridge.py"
    if not target.is_file():
        print("ERROR: Run this script from the existing project root. Missing:")
        print(f"  {target}")
        return 2

    raw = target.read_bytes()
    try:
        source = raw.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        print(f"ERROR: Could not safely read UTF-8 source file: {exc}")
        return 2

    marker = "    santali_answer = translate_english_to_santali(english_answer)"
    if marker not in source:
        if "clean_santali_translation_format(" in source and "strip_markdown_before_translation(" in source:
            print("ALREADY APPLIED: Santali translation formatting fix is present.")
            return 0
        print("ERROR: The expected Santali translation call was not found. No files were changed.")
        return 2

    helper_marker = "def strip_markdown_before_translation(text: str) -> str:"
    helper_source = Path(__file__).read_text(encoding="utf-8")
    helpers_start = helper_source.index(helper_marker)
    helpers_end = helper_source.index("\n\ndef main() -> int:", helpers_start)
    helpers = helper_source[helpers_start:helpers_end].rstrip() + "\n\n\n"

    insert_anchor = "def ask_santali_question("
    if insert_anchor not in source:
        print("ERROR: Could not find ask_santali_question() anchor. No files were changed.")
        return 2

    updated = source.replace(insert_anchor, helpers + insert_anchor, 1)
    if "import re\n" not in updated:
        future_line = "from __future__ import annotations\n"
        if future_line in updated:
            updated = updated.replace(future_line, future_line + "\nimport re\n", 1)
        else:
            updated = "import re\n" + updated
    updated = updated.replace(
        marker,
        "    plain_english_answer = strip_markdown_before_translation(english_answer)\n"
        "    translated_answer = translate_english_to_santali(plain_english_answer)\n"
        "    santali_answer = clean_santali_translation_format(translated_answer)",
        1,
    )

    # Validate syntax before creating/replacing any project file.
    try:
        ast.parse(updated, filename=str(target))
    except SyntaxError as exc:
        print(f"ERROR: Generated patch failed syntax validation: {exc}. No files were changed.")
        return 2

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = target.with_name(f"{target.name}.pre_translation_format_fix_{stamp}.bak")
    shutil.copy2(target, backup)
    target.write_text(updated, encoding="utf-8", newline="")

    # Validate the actual written file too; restore the backup on any failure.
    try:
        ast.parse(target.read_text(encoding="utf-8"), filename=str(target))
    except Exception as exc:
        shutil.copy2(backup, target)
        print(f"ERROR: Post-write validation failed; original file restored: {exc}")
        return 2

    # Small offline regression check against the reported artifact pattern.
    sample = "**Artificial Intelligence**\n\n## Definition\n- Definition one\n* ###What it does-*\n*\n*\n##Summary"
    pre = strip_markdown_before_translation(sample)
    post = clean_santali_translation_format("* #\u1c5f\u1c68\u1c74\n*\n* ###\u1c5f\u1c68")
    if "**" in pre or "##" in pre or re.search(r"(?m)^\s*[*-]\s*$", post):
        shutil.copy2(backup, target)
        print("ERROR: Offline regression check failed; original file restored.")
        return 2

    print("SUCCESS: Santali translation formatting fix applied and syntax-checked.")
    print("Updated: frontend\\api\\santali_chat_bridge.py")
    print(f"Backup:  {backup.relative_to(root)}")
    print("English Markdown is stripped before Santali translation; residual Markdown-only lines are cleaned afterward.")
    print("No backend, translation model, Groq, RAG, TTS, message renderer, or other-language path was changed.")
    print("Restart Streamlit before retesting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
