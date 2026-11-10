from __future__ import annotations

import py_compile
import shutil
from datetime import datetime
from pathlib import Path

MARKER = "SANTALI_OL_CHIKI_FINAL_DISPLAY_FIX_V2"
FONT_IMPORT = '@import url("https://fonts.googleapis.com/css2?family=Noto+Sans+Ol+Chiki&display=swap");'
OLD_FONT = r"font-family: \'Nirmala UI\', \'Noto Sans Ol Chiki\', sans-serif !important;"
NEW_FONT = r"font-family: \'Noto Sans Ol Chiki\', \'Nirmala UI\', sans-serif !important;"


def main() -> int:
    root = Path.cwd()
    target = root / "frontend" / "components" / "message.py"
    if not target.is_file():
        print("ERROR: frontend/components/message.py not found.")
        print("Run from C:\\Users\\kunda\\PycharmProjects\\multilingual-AITribalChatbot")
        return 2

    try:
        original = target.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as exc:
        print(f"ERROR: Could not read message.py as UTF-8; no changes made: {exc}")
        return 3

    if MARKER not in original:
        print("ERROR: the expected Santali final-display patch marker was not found; no changes made.")
        print("This patch is designed only for the currently patched message.py.")
        return 4

    updated = original
    if OLD_FONT in updated:
        updated = updated.replace(OLD_FONT, NEW_FONT, 1)
    elif NEW_FONT not in updated:
        print("ERROR: the expected font declaration was not found; no changes made.")
        print("Please don't manually replace the file; send the current message.py instead.")
        return 5

    # The previous Noto patch normally adds this import. Ensure it exists,
    # because the Ol Chiki-specific font must load before the CSS uses it.
    if FONT_IMPORT not in updated:
        style_anchor = "<style>\n"
        if style_anchor not in updated:
            print("ERROR: CSS style block not found; no changes made.")
            return 6
        updated = updated.replace(style_anchor, style_anchor + "        " + FONT_IMPORT + "\n", 1)

    if updated == original:
        print("Noto Sans Ol Chiki is already the first-choice font; no changes needed.")
        print("Please hard-refresh the Streamlit page with Ctrl+F5 after restarting Streamlit.")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = target.with_name(f"message.py.pre_santali_font_priority_{stamp}.bak")
    shutil.copy2(target, backup)
    target.write_text(updated, encoding="utf-8", newline="\n")

    try:
        py_compile.compile(str(target), doraise=True)
    except Exception as exc:
        shutil.copy2(backup, target)
        print(f"ERROR: syntax check failed; restored original from {backup.name}: {exc}")
        return 7

    print("SUCCESS: Santali font priority corrected and syntax-checked.")
    print("Ol Chiki uses Noto Sans Ol Chiki first; Nirmala UI remains only as a fallback.")
    print("Only frontend/components/message.py was modified.")
    print(f"Backup: {backup.relative_to(root)}")
    print("Restart Streamlit, then hard-refresh the browser with Ctrl+F5.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

