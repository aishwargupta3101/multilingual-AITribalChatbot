"""Safely add Santali to the main Streamlit language selector.

Run from the project root:
    python scripts/add_santali_to_language_selector.py

Only these files are changed, and only by adding missing entries:
    frontend/utils/constants.py
    frontend/components/sidebar.py
Original files are backed up to *.step17.bak before modification.
"""
from __future__ import annotations

import re
import shutil
import sys
from pathlib import Path


def main() -> int:
    project_root = Path.cwd()
    if not (project_root / "frontend/utils/constants.py").is_file():
        script_root = Path(__file__).resolve().parents[1]
        if (script_root / "frontend/utils/constants.py").is_file():
            project_root = script_root
        else:
            print("ERROR: Run this script from your project root; could not find frontend/utils/constants.py.")
            return 2

    constants_path = project_root / "frontend/utils/constants.py"
    sidebar_path = project_root / "frontend/components/sidebar.py"
    if not sidebar_path.is_file():
        print(f"ERROR: Required file not found: {sidebar_path}")
        return 2

    constants_text = constants_path.read_text(encoding="utf-8")
    sidebar_text = sidebar_path.read_text(encoding="utf-8")

    constants_changed = not re.search(r"(?m)^\s*['\"]santali['\"]\s*,?\s*$", constants_text)
    sidebar_changed = not re.search(r"(?m)^\s*['\"]santali['\"]\s*:", sidebar_text)

    # Validate all required insertion points before writing either file.
    if constants_changed and not re.search(r"(?m)^\s*['\"]monpa['\"]\s*,\s*$", constants_text):
        print("ERROR: Could not safely locate the Monpa entry in SUPPORTED_LANGUAGES; no files changed.")
        return 3
    if sidebar_changed and not re.search(r"(?m)^\s*['\"]monpa['\"]\s*:\s*['\"]Monpa['\"]\s*,\s*$", sidebar_text):
        print("ERROR: Could not safely locate the Monpa display-name entry; no files changed.")
        return 3

    new_constants = constants_text
    if constants_changed:
        new_constants = re.sub(
            r"(?m)^(\s*['\"]monpa['\"]\s*,\s*)$",
            lambda match: match.group(1) + '\n    "santali",',
            constants_text,
            count=1,
        )

    new_sidebar = sidebar_text
    if sidebar_changed:
        new_sidebar = re.sub(
            r"(?m)^(\s*['\"]monpa['\"]\s*:\s*['\"]Monpa['\"]\s*,\s*)$",
            lambda match: match.group(1) + '\n            "santali": "Santali (Experimental)",',
            sidebar_text,
            count=1,
        )

    # Confirm patch substitutions succeeded before touching disk.
    if constants_changed and '"santali"' not in new_constants and "'santali'" not in new_constants:
        print("ERROR: Could not add Santali to constants; no files changed.")
        return 4
    if sidebar_changed and '"santali"' not in new_sidebar and "'santali'" not in new_sidebar:
        print("ERROR: Could not add Santali display name; no files changed.")
        return 4

    changes = []
    for path, original, updated, changed in [
        (constants_path, constants_text, new_constants, constants_changed),
        (sidebar_path, sidebar_text, new_sidebar, sidebar_changed),
    ]:
        if changed and updated != original:
            backup = path.with_name(path.name + ".step17.bak")
            if not backup.exists():
                shutil.copy2(path, backup)
            changes.append((path, updated))

    for path, updated in changes:
        path.write_text(updated, encoding="utf-8", newline="")

    if not changes:
        print("Santali is already present in both the selector list and display-name mapping. No changes needed.")
    else:
        for path, _ in changes:
            print(f"Updated: {path.relative_to(project_root)}")
            print(f"Backup:  {path.relative_to(project_root)}.step17.bak")

    print("\nSantali now appears in the main selector as 'Santali (Experimental)'.")
    print("Important: the current validated Santali capability is experimental voice transcription only.")
    print("General Santali chat translation and text-to-speech are not established by this selector change.")
    print("Restart Streamlit to refresh the UI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
