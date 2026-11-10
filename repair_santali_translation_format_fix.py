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


def main() -> int:
    root = Path(__file__).resolve().parent
    target = root / "frontend" / "api" / "santali_chat_bridge.py"
    known_good_backup = target.with_name(
        "santali_chat_bridge.py.pre_translation_format_fix_20261019-130319.bak"
    )
    if not target.is_file():
        print(f"ERROR: Target file not found: {target}")
        return 2
    if not known_good_backup.is_file():
        print("ERROR: The pre-patch backup was not found; no files were changed.")
        print(f"Expected: {known_good_backup}")
        return 2

    # Use the backup made by the previous installer, rather than building on its syntax-broken output.
    try:
        source = known_good_backup.read_text(encoding="utf-8-sig")
        compile(source, str(known_good_backup), "exec")
    except Exception as exc:
        print(f"ERROR: The pre-patch backup is not valid Python: {exc}")
        print("No files were changed.")
        return 2

    marker = "    santali_answer = translate_english_to_santali(english_answer)"
    if marker not in source:
        print("ERROR: Backup does not contain the expected translation call.")
        print("No files were changed.")
        return 2
    if "from __future__ import annotations" in source:
        # Keep the future import in its original top-of-file position and add re only afterward.
        if not re.search(r"(?m)^import re\s*$", source):
            source = source.replace(
                "from __future__ import annotations",
                "from __future__ import annotations\n\nimport re",
                1,
            )
    elif not re.search(r"(?m)^import re\s*$", source):
        source = "import re\n" + source

    source = source.replace(
        marker,
        "    plain_english_answer = strip_markdown_before_translation(english_answer)\n"
        "    translated_answer = translate_english_to_santali(plain_english_answer)\n"
        "    santali_answer = clean_santali_translation_format(translated_answer)",
        1,
    )
    import inspect
    # Append helpers at EOF: definitions are after imports, so __future__ imports remain valid.
    if "def strip_markdown_before_translation(" in source or "def clean_santali_translation_format(" in source:
        print("ERROR: Backup unexpectedly already contains the formatting helpers; no files were changed.")
        return 2
    helper_block = "\n\n\n" + inspect.getsource(strip_markdown_before_translation).rstrip() + "\n\n\n" + inspect.getsource(clean_santali_translation_format).rstrip() + "\n"
    updated = source.rstrip() + helper_block + "\n"
    try:
        compile(updated, str(target), "exec")
    except SyntaxError as exc:
        print(f"ERROR: Corrected patch failed syntax validation: {exc}; no files were changed.")
        return 2

    # Preserve both the invalid current file and the original pre-patch backup.
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    damaged_backup = target.with_name(f"{target.name}.syntax_error_preserved_{stamp}.bak")
    shutil.copy2(target, damaged_backup)
    target.write_text(updated, encoding="utf-8", newline="")
    try:
        compile(target.read_text(encoding="utf-8"), str(target), "exec")
    except Exception as exc:
        # Restore the pre-patch working source, so the app can start again.
        shutil.copy2(known_good_backup, target)
        print(f"ERROR: Final validation failed; restored the pre-patch backup: {exc}")
        return 2

    print("SUCCESS: Repaired Santali bridge syntax and applied formatting cleanup.")
    print(f"Updated: {target.relative_to(root)}")
    print(f"Preserved broken version as: {damaged_backup.relative_to(root)}")
    print(f"Original pre-patch backup retained: {known_good_backup.relative_to(root)}")
    print("Only the Santali chat bridge was changed. Restart Streamlit before testing.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
