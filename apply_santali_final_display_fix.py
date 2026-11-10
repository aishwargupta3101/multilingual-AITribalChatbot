from __future__ import annotations

import py_compile
import re
import shutil
from datetime import datetime
from pathlib import Path

MARKER = "SANTALI_OL_CHIKI_FINAL_DISPLAY_FIX_V2"
ANCHOR = "    rendered_content = markdown_renderer.render(normalized_content)\n"
INSERTION = r'''    # SANTALI_OL_CHIKI_FINAL_DISPLAY_FIX_V2: bypass Markdown/font fallbacks for Ol Chiki only.
    _santali_language_key = str(language or "").strip().lower().replace("_", "-")
    _santali_display = (
        "santali" in _santali_language_key
        or _santali_language_key in {"sat", "sat-olck", "ol-chiki"}
        or any("\u1c50" <= _ch <= "\u1c7f" for _ch in str(content or ""))
    )
    if _santali_display:
        _santali_plain = normalize_assistant_markdown(content)
        _santali_plain = format_for_display(_santali_plain, language)
        # Remove Markdown that survived machine translation, plus empty list rows.
        _santali_plain = re.sub(r"(?m)^[ \t]*#{1,6}[ \t]*", "", _santali_plain)
        _santali_plain = re.sub(
            r"(?m)^[ \t]*(?:[-*+•◦▪●○]|\d+[.)])[ \t]*$\n?", "", _santali_plain
        )
        _santali_plain = re.sub(
            r"(?m)^[ \t]*(?:[-*+•◦▪●○]|\d+[.)])[ \t]+", "", _santali_plain
        )
        _santali_plain = re.sub(r"\*\*(.*?)\*\*", r"\1", _santali_plain)
        _santali_plain = re.sub(r"__(.*?)__", r"\1", _santali_plain)
        _santali_plain = re.sub(r"`([^`]*)`", r"\1", _santali_plain)
        _santali_plain = re.sub(r"(?m)^[ \t]+$", "", _santali_plain)
        _santali_plain = re.sub(r"\n{3,}", "\n\n", _santali_plain).strip()
        # Nirmala UI is available on Windows 10/11 and includes Ol Chiki glyphs.
        # Inline styling avoids depending on Google Fonts/network/CSS import behavior.
        rendered_content = (
            '<div lang="sat" dir="ltr" '
            'style="font-family: \'Nirmala UI\', \'Noto Sans Ol Chiki\', sans-serif !important; '
            'white-space: pre-wrap; line-height: 1.9;">'
            + escape(_santali_plain).replace("\n", "<br>")
            + "</div>"
        )
'''


def main() -> int:
    root = Path.cwd()
    target = root / "frontend" / "components" / "message.py"
    if not target.is_file():
        print("ERROR: frontend/components/message.py was not found.")
        print("Run this script from C:\\Users\\kunda\\PycharmProjects\\multilingual-AITribalChatbot.")
        return 2
    try:
        original = target.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        print(f"ERROR: Could not read message.py as UTF-8; no changes made: {exc}")
        return 3
    if MARKER in original:
        print("Santali final display fix is already applied; no changes made.")
        return 0
    if ANCHOR not in original:
        print("ERROR: expected Markdown-rendering line was not found; no changes made.")
        print("Please do not replace the file manually; this version of message.py differs from the expected structure.")
        return 4

    updated = original.replace(ANCHOR, ANCHOR + INSERTION, 1)
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = target.with_name(f"message.py.pre_santali_final_display_fix_{stamp}.bak")
    shutil.copy2(target, backup)
    target.write_text(updated, encoding="utf-8", newline="\n")
    try:
        py_compile.compile(str(target), doraise=True)
    except Exception as exc:
        shutil.copy2(backup, target)
        print(f"ERROR: syntax check failed; the original has been restored from {backup.name}: {exc}")
        return 5

    print("SUCCESS: final Santali display fix applied and syntax-checked.")
    print(f"Updated: {target.relative_to(root)}")
    print(f"Backup:  {backup.relative_to(root)}")
    print("Santali only: renders plain Ol Chiki with the Windows Nirmala UI fallback and removes empty Markdown bullets/headings.")
    print("No backend, translation model, Groq, RAG, TTS, or other-language code was changed.")
    print("Restart Streamlit (Ctrl+C, then run your usual Streamlit command) before retesting.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
