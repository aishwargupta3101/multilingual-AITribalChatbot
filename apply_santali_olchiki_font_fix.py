from __future__ import annotations

import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

MARKER = "SANTALI_OL_CHIKI_WEBFONT_FIX"
FONT_IMPORT = '@import url("https://fonts.googleapis.com/css2?family=Noto+Sans+Ol+Chiki&display=swap");'


def main() -> int:
    root = Path.cwd()
    target = root / "frontend" / "components" / "message.py"

    if not target.is_file():
        print("ERROR: frontend/components/message.py was not found.")
        print("Run this script from the multilingual-AITribalChatbot project root.")
        return 2

    original = target.read_text(encoding="utf-8-sig")
    updated = original

    if MARKER in updated:
        print("Santali Ol Chiki font fix is already applied; no changes made.")
        return 0

    # Add the web font import at the beginning of this component's style block.
    style_anchor = '        <style>\n'
    if style_anchor not in updated:
        print("ERROR: expected style block was not found in message.py; no changes made.")
        return 3
    updated = updated.replace(
        style_anchor,
        style_anchor + f"        {FONT_IMPORT}\n        /* {MARKER} */\n",
        1,
    )

    # Scope the font to Santali assistant messages only; leave all other language cards alone.
    css_anchor = "        .chat-row {\n"
    css_rule = (
        '        /* Ol Chiki requires an explicit script-capable font. */\n'
        '        .assistant-message.santali-script,\n'
        '        .assistant-message.santali-script * {\n'
        '            font-family: "Noto Sans Ol Chiki", sans-serif !important;\n'
        '        }\n'
    )
    if css_anchor not in updated:
        print("ERROR: expected chat-row CSS rule was not found; no changes made.")
        return 4
    updated = updated.replace(css_anchor, css_rule + css_anchor, 1)

    # Add a CSS class based on the existing message-language metadata.
    content_anchor = (
        "    rendered_content = markdown_renderer.render(normalized_content)\n\n"
        "    # Render the full assistant card in one HTML call to avoid nesting\n"
    )
    content_replacement = (
        "    rendered_content = markdown_renderer.render(normalized_content)\n\n"
        "    # {marker}: opt in only for Santali assistant cards.\n"
        "    language_key = str(language or \"\").strip().lower().replace(\"_\", \"-\")\n"
        "    language_class = (\n"
        "        \" santali-script\"\n"
        "        if language_key in {\"santali\", \"sat\", \"sat-olck\", \"ol-chiki\"}\n"
        "        else \"\"\n"
        "    )\n\n"
        "    # Render the full assistant card in one HTML call to avoid nesting\n"
    ).replace("{marker}", MARKER)
    if content_anchor not in updated:
        print("ERROR: expected message-rendering anchor was not found; no changes made.")
        return 5
    updated = updated.replace(content_anchor, content_replacement, 1)

    html_anchor = '                <div class="assistant-message">\n'
    if html_anchor not in updated:
        print("ERROR: expected assistant-message element was not found; no changes made.")
        return 6
    updated = updated.replace(
        html_anchor,
        '                <div class="assistant-message{language_class}">\n',
        1,
    )

    # Save one immutable backup before changing the user's existing module.
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = target.with_name(f"message.py.pre_santali_font_fix_{stamp}.bak")
    shutil.copy2(target, backup)
    target.write_text(updated, encoding="utf-8", newline="\n")

    # Syntax-check the changed file before declaring success. Restore original if it fails.
    import py_compile
    try:
        py_compile.compile(str(target), doraise=True)
    except Exception as exc:
        shutil.copy2(backup, target)
        print(f"ERROR: syntax check failed; original restored from {backup.name}: {exc}")
        return 7

    print("SUCCESS: Ol Chiki web-font fix applied to the existing project.")
    print(f"Updated: {target.relative_to(root)}")
    print(f"Backup:  {backup.relative_to(root)}")
    print("Only Santali assistant-message cards use Noto Sans Ol Chiki; other languages are unchanged.")
    print("Restart Streamlit and test the same Santali question again.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
