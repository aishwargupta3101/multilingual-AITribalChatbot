"""Add Gondi MMS speech + local mT5 translation to the existing Tribal AI project.

Run from the repository root after extracting the full integration ZIP there.
The installer changes only Gondi-specific modules plus the existing language
selector/chat/voice/router wiring. Every pre-existing modified file is backed up.
"""
from __future__ import annotations

import codecs
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PAYLOAD = PACKAGE_ROOT / "gondi_mms_payload"
ROUTER_IMPORT = "from backend.tribal_languages.gondi_language_router import router as gondi_language_router"
CHAT_MARKER = "GONDI_TEXT_CHAT_ROUTING"
VOICE_MARKER = "GONDI_MMS_VOICE_ROUTING"


def read_text(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        value = raw.decode("utf-16")
    elif raw.startswith(codecs.BOM_UTF8):
        value = raw.decode("utf-8-sig")
    else:
        value = raw.decode("utf-8")
    return value.replace("\r\n", "\n")


def backup_path(path: Path) -> Path:
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    candidate = path.with_name(f"{path.name}.pre_gondi_mms_mt5_{stamp}.bak")
    index = 1
    while candidate.exists():
        candidate = path.with_name(f"{path.name}.pre_gondi_mms_mt5_{stamp}_{index}.bak")
        index += 1
    shutil.copy2(path, candidate)
    return candidate


def patch_constants(text: str) -> str:
    start = text.find("SUPPORTED_LANGUAGES")
    if start < 0:
        raise ValueError("Could not locate SUPPORTED_LANGUAGES in frontend/utils/constants.py")
    left = text.find("[", start)
    right = text.find("]", left + 1)
    if left < 0 or right < 0:
        raise ValueError("Could not safely locate the SUPPORTED_LANGUAGES list.")
    body = text[left + 1:right]
    if re.search(r"(?i)['\"]gondi['\"]", body):
        return text
    line_anchor = None
    for anchor in ("santali", "monpa", "tai_khamti", "manipuri", "hindi"):
        match = re.search(rf"(?i)['\"]{re.escape(anchor)}['\"]", body)
        if match:
            line_anchor = match.end()
            break
    if line_anchor is None:
        raise ValueError("Could not find a safe language entry after which to add Gondi.")
    line_end = body.find("\n", line_anchor)
    if line_end < 0:
        line_end = len(body)
    updated = body[:line_end] + '\n    "gondi",  # GONDI_MMS_MT5' + body[line_end:]
    return text[:left + 1] + updated + text[right:]


def patch_sidebar(text: str) -> str:
    pattern = re.compile(r"(?mi)^([ \t]*['\"]gondi['\"]\s*:\s*)['\"][^'\"]*['\"]([ \t]*,?)$")
    match = pattern.search(text)
    if match:
        replacement = match.group(1) + '"Gondi (Adilabad)"' + match.group(2)
        return text[:match.start()] + replacement + text[match.end():]
    anchor_pattern = re.compile(r"(?mi)^([ \t]*['\"](?:santali|monpa|tai_khamti)['\"]\s*:\s*['\"][^'\"]*['\"]\s*,?)$")
    match = anchor_pattern.search(text)
    if not match:
        # Some versions define the selector from constants and don't hold a label map.
        if "SUPPORTED_LANGUAGES" in text and "language.replace" in text:
            return text
        raise ValueError("Could not safely add the Gondi label to frontend/components/sidebar.py")
    line = match.group(1).rstrip()
    if not line.endswith(","):
        line += ","
    return text[:match.end()] + '\n            "gondi": "Gondi (Adilabad)",' + text[match.end():]


def patch_chat_box(text: str) -> str:
    if CHAT_MARKER not in text:
        start = text.find("def ask_ai(question):")
        if start < 0:
            raise ValueError("Could not find ask_ai(question) in frontend/components/chat_box.py")
        try_pos = text.find("    try:\n", start)
        next_def = text.find("\ndef ", start + 5)
        if try_pos < 0 or (next_def >= 0 and try_pos > next_def):
            raise ValueError("Could not locate ask_ai()'s try block for safe Gondi routing.")
        branch = (
            f"    # {CHAT_MARKER}: Gondi uses local Hindi-Gondi MT plus the existing English chat/RAG.\n"
            '    if get_language().strip().lower() == "gondi":\n'
            '        from api.gondi_chat_bridge import ask_gondi_question\n'
            '        return ask_gondi_question(\n'
            '            question=question,\n'
            '            session_id=st.session_state.session_id,\n'
            '            source_language=st.session_state.get("gondi_input_language", "English"),\n'
            '        )\n'
        )
        text = text[:try_pos] + branch + text[try_pos:]
    ui_marker = "GONDI_INPUT_LANGUAGE_SELECTOR"
    if ui_marker not in text:
        anchor = "    user_input = st.chat_input("
        pos = text.find(anchor)
        if pos < 0:
            raise ValueError("Could not find st.chat_input() in frontend/components/chat_box.py")
        ui = (
            f"    # {ui_marker}: explicit source language for Gondi; no additional per-session toggle.\n"
            '    if get_language().strip().lower() == "gondi":\n'
            '        st.caption("Gondi text uses the local fine-tuned Hindi-Gondi model. Train it before translation; speech is available in Voice Assistant.")\n'
            '        st.selectbox("Question language", ["English", "Gondi"], index=0, key="gondi_input_language")\n'
        )
        text = text[:pos] + ui + text[pos:]
    text = text.replace(
        "Gondi text chat uses Bhashini translation. Gondi voice input/output is not enabled yet because a compatible model is not configured.",
        "Gondi text uses the local fine-tuned Hindi-Gondi model (train it first). The Voice Assistant uses experimental MMS Adilabad Gondi models.",
    )
    text = text.replace(
        "Gondi text chat uses Bhashini translation.",
        "Gondi text uses the local fine-tuned Hindi-Gondi model (training required before translation).",
    )
    return text


def patch_main(text: str) -> str:
    if ROUTER_IMPORT not in text:
        # Insert near another tribal-language router import if possible.
        import_lines = [
            line for line in text.splitlines()
            if line.lstrip().startswith("from ") and "tribal_languages" in line and "router" in line
        ]
        if import_lines:
            line = import_lines[-1]
            text = text.replace(line, line + "\n" + ROUTER_IMPORT, 1)
        else:
            anchor = "app = FastAPI("
            pos = text.find(anchor)
            if pos < 0:
                raise ValueError("Could not find FastAPI app construction in backend/main.py")
            text = text[:pos] + ROUTER_IMPORT + "\n" + text[pos:]
    if "app.include_router(gondi_language_router)" not in text:
        anchor = "app.include_router(tribal_language_lab_router)"
        if anchor in text:
            text = text.replace(anchor, anchor + "\napp.include_router(gondi_language_router)", 1)
        else:
            anchor = "app.include_router(api_router)"
            if anchor in text:
                text = text.replace(anchor, anchor + "\napp.include_router(gondi_language_router)", 1)
            else:
                raise ValueError("Could not safely register the Gondi router in backend/main.py")
    return text


def patch_voice(text: str) -> str:
    if VOICE_MARKER in text:
        return text
    anchor = "def show_voice_page():"
    pos = text.find(anchor)
    if pos < 0:
        raise ValueError("Could not find show_voice_page() in frontend/views/voice.py")
    end = text.find("\n", pos)
    branch = (
        f"\n    # {VOICE_MARKER}: use the additive Gondi view; all existing language voice flows continue below.\n"
        '    _selected_voice_language = str(st.session_state.get("language", "english")).strip().lower().replace("-", "_")\n'
        '    if _selected_voice_language in {"gondi", "gon"}:\n'
        '        try:\n'
        '            from views.gondi_voice import show_gondi_voice_page\n'
        '        except ModuleNotFoundError:\n'
        '            from frontend.views.gondi_voice import show_gondi_voice_page\n'
        '        show_gondi_voice_page()\n'
        '        return\n'
    )
    return text[:end] + branch + text[end:]


def main() -> int:
    project = Path.cwd().resolve()
    if not (project / "frontend").is_dir() or not (project / "backend").is_dir():
        print("ERROR: Run this installer from the existing multilingual-AITribalChatbot project root.")
        return 2
    marker = project / "scripts" / ".gondi_mms_mt5_installed"
    if not PAYLOAD.is_dir():
        if marker.exists():
            print("Gondi MMS/mT5 integration is already installed; no payload files found.")
            return 0
        print("ERROR: Integration payload missing. Extract the full ZIP into the project root, preserving folders.")
        return 2

    required = [
        project / "frontend/utils/constants.py",
        project / "frontend/components/sidebar.py",
        project / "frontend/components/chat_box.py",
        project / "frontend/views/voice.py",
        project / "backend/main.py",
    ]
    missing = [str(path.relative_to(project)) for path in required if not path.is_file()]
    if missing:
        print("ERROR: Required files missing; no source files were changed:")
        print("\n".join(f" - {item}" for item in missing))
        return 2

    module_map = {
        "backend/tribal_languages/gondi_local_translation_service.py": PAYLOAD / "backend/tribal_languages/gondi_local_translation_service.py",
        "backend/tribal_languages/gondi_mms_service.py": PAYLOAD / "backend/tribal_languages/gondi_mms_service.py",
        "backend/tribal_languages/gondi_language_router.py": PAYLOAD / "backend/tribal_languages/gondi_language_router.py",
        "frontend/api/gondi_translation.py": PAYLOAD / "frontend/api/gondi_translation.py",
        "frontend/api/gondi_chat_bridge.py": PAYLOAD / "frontend/api/gondi_chat_bridge.py",
        "frontend/api/gondi_speech.py": PAYLOAD / "frontend/api/gondi_speech.py",
        "frontend/views/gondi_voice.py": PAYLOAD / "frontend/views/gondi_voice.py",
        "scripts/download_gondi_adibhasha.py": PAYLOAD / "scripts/download_gondi_adibhasha.py",
        "scripts/train_gondi_mt5.py": PAYLOAD / "scripts/train_gondi_mt5.py",
        "tests/test_gondi_mms_integration.py": PAYLOAD / "tests/test_gondi_mms_integration.py",
    }
    patched = {
        project / "frontend/utils/constants.py": lambda s: patch_constants(s),
        project / "frontend/components/sidebar.py": lambda s: patch_sidebar(s),
        project / "frontend/components/chat_box.py": lambda s: patch_chat_box(s),
        project / "frontend/views/voice.py": lambda s: patch_voice(s),
        project / "backend/main.py": lambda s: patch_main(s),
    }

    try:
        copy_texts = {project / rel: source.read_text(encoding="utf-8") for rel, source in module_map.items()}
        patched_texts = {path: patcher(read_text(path)) for path, patcher in patched.items()}
        for path, value in copy_texts.items():
            compile(value, str(path), "exec")
        for path, value in patched_texts.items():
            compile(value, str(path), "exec")
    except Exception as exc:
        print(f"ERROR: Preflight failed; no files were written: {type(exc).__name__}: {exc}")
        return 2

    # Preserve the original versions and prepare all directories before writing.
    backups: list[tuple[Path, Path]] = []
    changed: list[Path] = []
    try:
        for path in list(copy_texts) + list(patched_texts):
            path.parent.mkdir(parents=True, exist_ok=True)
        for path, content in copy_texts.items():
            encoded = content.encode("utf-8")
            if path.exists() and path.read_bytes() == encoded:
                continue
            backup = backup_path(path) if path.exists() else None
            if backup:
                backups.append((path, backup))
            path.write_bytes(encoded)
            changed.append(path)
        for path, content in patched_texts.items():
            current = read_text(path)
            if current == content:
                continue
            backup = backup_path(path)
            backups.append((path, backup))
            path.write_text(content, encoding="utf-8", newline="\n")
            changed.append(path)
        # Final syntax validation after writes. Roll back changed files if this fails.
        for path in changed:
            if path.suffix == ".py":
                compile(read_text(path), str(path), "exec")
    except Exception as exc:
        print(f"ERROR: Write/syntax check failed: {type(exc).__name__}: {exc}")
        for path, backup in reversed(backups):
            try:
                shutil.copy2(backup, path)
            except OSError:
                pass
        print("Attempted rollback from the backups listed below.")
        for _, backup in backups:
            print(f" - {backup}")
        return 2

    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text("Gondi MMS speech + local MT5 integration installed.\n", encoding="utf-8")
    print("SUCCESS: Gondi MMS + local mT5 integration installed and syntax-checked.")
    if changed:
        print("Updated / added:")
        for path in changed:
            print(f" - {path.relative_to(project)}")
    else:
        print("All target files were already current.")
    if backups:
        print("Backups created:")
        for _, backup in backups:
            print(f" - {backup.name}")
    print("No Bhashini credentials or new requirements file are needed.")
    print("Next: accept AdiBhasha's access terms, run scripts/download_gondi_adibhasha.py, then train scripts/train_gondi_mt5.py.")
    print("MMS ASR/TTS weights download lazily on first use; Gondi speech quality is experimental.")
    try:
        shutil.rmtree(PAYLOAD)
    except OSError:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
