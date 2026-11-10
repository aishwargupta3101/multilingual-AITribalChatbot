from __future__ import annotations

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

MARKER = "SANTALI_MARKDOWN_DISPLAY_CLEANUP_V1"
ANCHOR = "    normalized_content = format_for_display(normalized_content, language)\n"

INSERTION = '''    normalized_content = format_for_display(normalized_content, language)

    # SANTALI_MARKDOWN_DISPLAY_CLEANUP_V1: translated Markdown markers can
    # survive translation or leave empty list items. Clean only Santali cards.
    language_key = str(language or "").strip().lower().replace("_", "-")
    if "santali" in language_key or language_key in {"sat", "sat-olck", "ol-chiki"}:
        # Remove heading markers, including stray doubled hashes left mid-line.
        normalized_content = re.sub(r"(?m)^\\s*#{1,6}\\s*", "", normalized_content)
        normalized_content = re.sub(r"#{2,}", "", normalized_content)

        # Convert list items to plain lines so untranslated/empty Markdown
        # bullets do not appear as blank rows in the answer card.
        normalized_content = re.sub(
            r"(?m)^\\s*(?:[-*+•◦▪●○]\\s+|\\d+[.)]\\s+)",
            "",
            normalized_content,
        )
        # Remove list-marker-only rows after translation.
        normalized_content = re.sub(
            r"(?m)^\\s*(?:[-*+•◦▪●○]|\\d+[.)])\\s*$\\n?",
            "",
            normalized_content,
        )
        normalized_content = re.sub(r"(?m)^[ \\t]+$", "", normalized_content)
        normalized_content = re.sub(r"\\n[ \\t]*\\n(?:[ \\t]*\\n)+", "\\n\\n", normalized_content)
        normalized_content = normalized_content.strip()

'''


def main() -> int:
    root = Path.cwd()
    target = root / "frontend" / "components" / "message.py"
    if not target.is_file():
        print("ERROR: frontend/components/message.py was not found.")
        print("Run this script from the multilingual-AITribalChatbot project root.")
        return 2

    try:
        original = target.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        print(f"ERROR: Could not read message.py as UTF-8; no changes made: {exc}")
        return 3

    if MARKER in original:
        print("Santali Markdown cleanup is already applied; no changes made.")
        return 0
    if ANCHOR not in original:
        print("ERROR: expected format_for_display anchor was not found; no changes made.")
        print("No files were changed. Please send the current frontend/components/message.py.")
        return 4

    updated = original.replace(ANCHOR, INSERTION, 1)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = target.with_name(f"message.py.pre_santali_markdown_fix_{stamp}.bak")
    shutil.copy2(target, backup)
    target.write_text(updated, encoding="utf-8", newline="\n")

    import py_compile
    try:
        py_compile.compile(str(target), doraise=True)
    except Exception as exc:
        shutil.copy2(backup, target)
        print(f"ERROR: syntax check failed; original restored from {backup.name}: {exc}")
        return 5

    print("SUCCESS: Santali Markdown display cleanup applied.")
    print(f"Updated: {target.relative_to(root)}")
    print(f"Backup:  {backup.relative_to(root)}")
    print("Scope: Santali answer display only; other languages and backend services are unchanged.")
    print("Restart Streamlit before testing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
