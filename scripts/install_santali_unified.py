"""Install the unified Santali language integration into the existing project.

Run from the project root after extracting the package there:
    python scripts/install_santali_unified.py
The installer backs up modified project files and aborts before writes if key anchors
cannot be found. It is idempotent for already-patched source files.
"""
from __future__ import annotations

import codecs
import re
import shutil
import sys
from pathlib import Path

PACKAGE_ROOT = Path(__file__).resolve().parents[1]
PAYLOAD_ROOT = PACKAGE_ROOT / "santali_unified_payload"
MARKER = "SANTALI_UNIFIED_CHAT_ROUTING"


def read_text(path: Path) -> str:
    """Read normal UTF-8 source files and Windows UTF-16 requirement/.env files safely."""
    raw = path.read_bytes()
    if raw.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE)):
        return raw.decode("utf-16")
    if raw.startswith(codecs.BOM_UTF8):
        text = raw.decode("utf-8-sig")
    else:
        text = raw.decode("utf-8")
    # Normalize Windows CRLF before exact-anchor patching.
    return text.replace("\r\n", "\n").replace("\r", "\n")


def backup_once(path: Path, label: str = "santali_unified") -> Path:
    backup = path.with_name(path.name + f".{label}.bak")
    if not backup.exists():
        shutil.copy2(path, backup)
    return backup


def patch_chat_box(text: str) -> tuple[str, bool]:
    new_text = text
    if MARKER not in new_text:
        start = new_text.find("def ask_ai(question):")
        end = new_text.find("def ask_ai_stream(", start + 1)
        if start < 0 or end < 0:
            raise ValueError("Could not find ask_ai() and ask_ai_stream() in frontend/components/chat_box.py")
        segment = new_text[start:end]
        anchor = "    try:\n"
        pos = segment.find(anchor)
        if pos < 0:
            raise ValueError("Could not find the try block inside ask_ai(); no chat_box.py changes were applied.")
        inserted = (
            f"    # {MARKER}: route Santali-output chat through the shared translation -> chat -> Santali path.\n"
            "    if get_language().strip().lower() == \"santali\":\n"
            "        from api.santali_chat_bridge import ask_santali_question\n"
            "        return ask_santali_question(\n"
            "            question=question,\n"
            "            session_id=st.session_state.session_id,\n"
            "        )\n"
        )
        segment = segment[:pos] + inserted + segment[pos:]
        new_text = new_text[:start] + segment + new_text[end:]

    # Add a play button for Santali assistant messages while leaving all existing actions intact.
    audio_anchor = "            render_images(images)\n"
    if "santali_tts_audio_" not in new_text:
        pos2 = new_text.find(audio_anchor, new_text.find("def show_chat_box"))
        if pos2 < 0:
            raise ValueError("Could not find assistant-message rendering anchor in chat_box.py")
        pos2 += len(audio_anchor)
        tts_ui = (
            "            if str(message.get(\"language\", \"\")).lower() == \"santali\":\n"
            "                santali_audio_key = f\"santali_tts_audio_{index}\"\n"
            "                if st.button(\"🔊 Speak Santali answer\", key=f\"santali_tts_button_{index}\"):\n"
            "                    try:\n"
            "                        from api.santali_tts import synthesize_santali_wav\n"
            "                        with st.spinner(\"Generating Santali speech...\"):\n"
            "                            st.session_state[santali_audio_key] = synthesize_santali_wav(content)\n"
            "                    except Exception as tts_error:\n"
            "                        st.error(f\"Santali speech generation failed: {type(tts_error).__name__}: {tts_error}\")\n"
            "                if st.session_state.get(santali_audio_key):\n"
            "                    st.audio(st.session_state[santali_audio_key], format=\"audio/wav\")\n"
        )
        new_text = new_text[:pos2] + tts_ui + new_text[pos2:]

    # Explain the selected output language and permit either English or Ol Chiki as typed input.
    guidance_marker = "SANTALI_UNIFIED_INPUT_GUIDANCE"
    if guidance_marker not in new_text:
        input_anchor = "    user_input = st.chat_input("
        input_pos = new_text.find(input_anchor, new_text.find("def show_chat_box"))
        if input_pos < 0:
            raise ValueError("Could not find the normal chat input to add Santali output-language guidance.")
        guidance = (
            "    # SANTALI_UNIFIED_INPUT_GUIDANCE: Santali is the reply language.\n"
            "    if get_language().strip().lower() == \"santali\":\n"
            "        st.caption(\"Reply language: Santali (Ol Chiki). Type your question in English or Ol Chiki; answers are returned in Santali.\")\n"
        )
        new_text = new_text[:input_pos] + guidance + new_text[input_pos:]
    return new_text, new_text != text

def patch_voice(text: str) -> tuple[str, bool]:
    """Route Santali voice mode without relying on one exact session_id assignment.

    The user's current voice.py may have changed across earlier iterations, so the
    branch is installed at the entry to show_voice_page() and initializes its own
    session ID. Non-Santali requests fall through to the original function.
    """
    original = text
    marker = "SANTALI_UNIFIED_VOICE_ROUTING"
    if marker not in text:
        function_match = re.search(r"(?m)^def\s+show_voice_page\s*\(\s*\)\s*:\s*$", text)
        if not function_match:
            raise ValueError("Could not find def show_voice_page() in frontend/views/voice.py")
        insertion = function_match.end()
        # Consume the function line's newline, leaving its body after the inserted block.
        if insertion < len(text) and text[insertion] == "\n":
            insertion += 1
        branch = (
            "    # SANTALI_UNIFIED_VOICE_ROUTING: use the global language selector; no checkbox needed.\n"
            "    language = st.session_state.get(\"language\", \"english\")\n"
            "    if \"session_id\" not in st.session_state:\n"
            "        import uuid\n"
            "        st.session_state[\"session_id\"] = str(uuid.uuid4())\n"
            "    session_id = st.session_state[\"session_id\"]\n"
            "    use_santali_onnx = False  # compatibility for older code paths after removing the opt-in UI\n"
            "    if str(language).strip().lower() == \"santali\":\n"
            "        from views.santali_voice import show_santali_voice_page\n"
            "        show_santali_voice_page(session_id)\n"
            "        return\n\n"
        )
        text = text[:insertion] + branch + text[insertion:]

    # Remove the obsolete Santali experiment UI. Santali now routes above to the
    # integrated voice page; other languages should not see a checkbox for it.
    start_patterns = [
        r"(?m)^[ \t]*# This is a separate opt-in voice-test mode\.",
        r"(?m)^[ \t]*# This is a separate opt-in voice-test mode\. It does not add Santali",
        r"(?m)^[ \t]*st\.markdown\(\"#### Experimental Santali Speech Recognition\"\)",
    ]
    exp_start = None
    for pattern in start_patterns:
        found = re.search(pattern, text)
        if found:
            exp_start = found.start()
            break
    end_anchor = '    html_block(\n        """\n        <div class="voice-record-card">'
    if exp_start is not None:
        exp_end = text.find(end_anchor, exp_start)
        if exp_end < 0:
            raise ValueError("Found the old Santali opt-in UI but could not safely locate the regular voice recorder section.")
        text = text[:exp_start] + text[exp_end:]

    # Remove stale import only if present; all other imports and existing voice paths remain.
    text = text.replace("from api.santali_chat_bridge import translate_and_ask_santali\n", "")
    return text, text != original

def patch_selector(constants_text: str, sidebar_text: str) -> tuple[str, str, bool, bool]:
    """Add Santali robustly to the existing language list and label mapping."""
    original_constants, original_sidebar = constants_text, sidebar_text

    if not re.search(r"(?i)['\"]santali['\"]", constants_text):
        list_match = re.search(
            r"(?s)(SUPPORTED_LANGUAGES\s*=\s*\[)(.*?)(\])",
            constants_text,
        )
        if list_match:
            body = list_match.group(2)
            if not re.search(r"(?i)['\"]monpa['\"]", body):
                raise ValueError("Could not safely add Santali: no Monpa entry in SUPPORTED_LANGUAGES constants.")
            trimmed = body.rstrip()
            if trimmed and not trimmed.endswith(","):
                trimmed += ","
            updated_body = trimmed + '\n    "santali",\n'
            constants_text = (
                constants_text[:list_match.start(2)]
                + updated_body
                + constants_text[list_match.end(2):]
            )
        else:
            # Preserve support for the previous one-value-per-line representation.
            if not re.search(r"(?mi)^\s*['\"]monpa['\"]\s*,\s*$", constants_text):
                raise ValueError("Could not safely add Santali: no Monpa entry in SUPPORTED_LANGUAGES constants.")
            constants_text = re.sub(
                r"(?m)^(\s*['\"]monpa['\"]\s*,\s*)$",
                lambda m: m.group(1) + '\n    "santali",',
                constants_text,
                count=1,
            )

    sidebar_text = re.sub(
        r"Santali\s*\(Experimental\)", "Santali (Ol Chiki)", sidebar_text, flags=re.IGNORECASE
    )
    if not re.search(r"(?i)['\"]santali['\"]\s*:", sidebar_text):
        label_match = re.search(r"(['\"]monpa['\"]\s*:\s*['\"]Monpa['\"]\s*,?)", sidebar_text)
        if not label_match:
            raise ValueError("Could not safely add Santali: no Monpa display-name entry in sidebar.py.")
        label_entry = label_match.group(1).rstrip()
        if not label_entry.endswith(","):
            label_entry += ","
        label_entry += '\n            "santali": "Santali (Ol Chiki)",'
        sidebar_text = sidebar_text[:label_match.start(1)] + label_entry + sidebar_text[label_match.end(1):]

    # If the key existed with prototype wording, normalize just its mapping line.
    sidebar_text = re.sub(
        r"(?mi)^([ \t]*['\"]santali['\"]\s*:\s*)['\"][^'\"]*['\"]([ \t]*,?)$",
        lambda m: m.group(1) + '"Santali (Ol Chiki)"' + m.group(2),
        sidebar_text,
        count=1,
    )
    return (
        constants_text,
        sidebar_text,
        constants_text != original_constants,
        sidebar_text != original_sidebar,
    )


def patch_router(text: str) -> tuple[str, bool]:
    pattern = re.compile(r"def _enabled\(\) -> bool:\n.*?(?=\n\ndef _get_service\()", re.DOTALL)
    match = pattern.search(text)
    if not match:
        raise ValueError("Could not find _enabled() in backend/tribal_languages/santali_onnx_router.py")
    new_function = '''def _enabled() -> bool:
    """Santali is available by default; explicit false remains an administrative kill switch."""
    value = os.getenv("TRIBAL_SANTALI_ONNX_STT_ENABLED", "true").strip().lower()
    return value not in {"0", "false", "no", "off", "disabled"}'''
    new_text = text[:match.start()] + new_function + text[match.end():]
    # Keep status text aligned with the new default behavior.
    new_text = new_text.replace(
        '"A single Common Voice smoke test completed. This route remains disabled by default; "\n            "broader accuracy and native-speaker review are still required."',
        '"Enabled for normal Santali language selection. Recognition is still machine-generated; "\n            "broader accuracy and native-speaker review are required before production claims."',
    )
    new_text = new_text.replace(
        '"Santali ONNX STT is disabled. Set TRIBAL_SANTALI_ONNX_STT_ENABLED=true "\n                "only for a controlled experiment after review."',
        '"Santali ONNX STT is administratively disabled. Remove the explicit false setting or set "\n                "TRIBAL_SANTALI_ONNX_STT_ENABLED=true to enable the normal Santali language flow."',
    )
    return new_text, new_text != text


def patch_main(text: str) -> tuple[str, bool]:
    original = text
    onnx_import = "from backend.tribal_languages.santali_onnx_router import router as santali_onnx_router"
    language_import = "from backend.tribal_languages.santali_language_router import router as santali_language_router"

    if "santali_onnx_router" not in text:
        anchor = "from backend.tribal_languages.router import router as tribal_language_lab_router"
        if anchor in text:
            text = text.replace(anchor, anchor + "\n" + onnx_import, 1)
        else:
            text = onnx_import + "\n" + text
        onnx_imported = True
    else:
        onnx_imported = "from backend.tribal_languages.santali_onnx_router import" in text

    if "santali_language_router" not in text:
        if onnx_imported and onnx_import in text:
            text = text.replace(onnx_import, onnx_import + "\n" + language_import, 1)
        elif "from backend.tribal_languages.router import router as tribal_language_lab_router" in text:
            anchor = "from backend.tribal_languages.router import router as tribal_language_lab_router"
            text = text.replace(anchor, anchor + "\n" + language_import, 1)
        else:
            text = language_import + "\n" + text

    if "app.include_router(santali_onnx_router)" not in text:
        include_anchor = "app.include_router(tribal_language_lab_router)"
        if include_anchor in text:
            text = text.replace(include_anchor, include_anchor + "\napp.include_router(santali_onnx_router)", 1)
        elif "app.include_router(api_router)" in text:
            text = text.replace("app.include_router(api_router)", "app.include_router(api_router)\napp.include_router(santali_onnx_router)", 1)
        else:
            raise ValueError("Could not locate an app.include_router(...) insertion point in backend/main.py")

    if "app.include_router(santali_language_router)" not in text:
        if "app.include_router(santali_onnx_router)" in text:
            anchor = "app.include_router(santali_onnx_router)"
            text = text.replace(anchor, anchor + "\napp.include_router(santali_language_router)", 1)
        elif "app.include_router(api_router)" in text:
            text = text.replace("app.include_router(api_router)", "app.include_router(api_router)\napp.include_router(santali_language_router)", 1)
        else:
            raise ValueError("Could not locate an app.include_router(...) insertion point for Santali translation/TTS.")
    return text, text != original


def update_env(env_path: Path) -> bool:
    if not env_path.exists():
        return False
    text = read_text(env_path)
    pattern = re.compile(r"(?m)^\s*TRIBAL_SANTALI_ONNX_STT_ENABLED\s*=\s*[^\r\n]*$")
    if pattern.search(text):
        updated = pattern.sub("TRIBAL_SANTALI_ONNX_STT_ENABLED=true", text, count=1)
        if updated != text:
            backup_once(env_path)
            env_path.write_text(updated, encoding="utf-8", newline="")
            return True
    return False


def append_missing_dependencies(path: Path) -> bool:
    if not path.is_file():
        return False
    raw = path.read_bytes()
    text = read_text(path)
    # PowerShell/Windows editors sometimes save requirements.txt as UTF-16LE.
    # pip expects UTF-8 text; normalize with a backup even if no dependency is missing.
    normalize_encoding = raw.startswith((codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE))
    existing = set()
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith(("-", "http:", "https:")):
            continue
        name = re.split(r"[<=>!~;\[]", line, maxsplit=1)[0].strip().lower().replace("_", "-")
        if name:
            existing.add(name)
    required = [
        "onnx-asr[cpu,hub]",
        "av",
        "onnxruntime",
        "huggingface_hub",
        "IndicTransToolkit",
        "transformers<5",
        "sentencepiece",
        "soundfile",
        "numpy",
        "torch",
        "python-dotenv",
        "psutil",
        "python-multipart",
        "requests",
    ]
    add = []
    for spec in required:
        name = re.split(r"[<=>!~;\[]", spec, maxsplit=1)[0].strip().lower().replace("_", "-")
        if name not in existing:
            add.append(spec)
            existing.add(name)
    if not add and not normalize_encoding:
        return False
    backup_once(path)
    if add:
        updated = text.rstrip() + "\n\n# Santali STT + bidirectional translation + Santali Piper TTS\n" + "\n".join(add) + "\n"
    else:
        updated = text
    path.write_text(updated, encoding="utf-8", newline="")
    return True


def main() -> int:
    project_root = Path.cwd()
    if not (project_root / "frontend").is_dir() and (PACKAGE_ROOT / "frontend").is_dir():
        project_root = PACKAGE_ROOT
    payload = PAYLOAD_ROOT
    install_marker = project_root / "scripts" / ".santali_unified_installed_v3"
    if not payload.is_dir():
        if install_marker.exists():
            print("Santali unified integration was already installed in this project.")
            print("The staging payload was removed after the successful install to keep the project tree clean.")
            return 0
        print(f"ERROR: Installer payload not found: {payload}. Extract the full ZIP into the project root and rerun.")
        return 2

    required = [
        project_root / "frontend/components/chat_box.py",
        project_root / "frontend/views/voice.py",
        project_root / "frontend/utils/constants.py",
        project_root / "frontend/components/sidebar.py",
        project_root / "backend/main.py",
    ]
    missing = [str(p.relative_to(project_root)) for p in required if not p.is_file()]
    if missing:
        print("ERROR: Required project files are missing; no integration applied:")
        for name in missing:
            print(" -", name)
        return 2

    changes: list[tuple[Path, str]] = []
    try:
        # Precompute and validate every patch before writing code files.
        chat_path = project_root / "frontend/components/chat_box.py"
        voice_path = project_root / "frontend/views/voice.py"
        constants_path = project_root / "frontend/utils/constants.py"
        sidebar_path = project_root / "frontend/components/sidebar.py"
        router_path = project_root / "backend/tribal_languages/santali_onnx_router.py"
        main_path = project_root / "backend/main.py"

        chat_new, chat_changed = patch_chat_box(read_text(chat_path))

        # Recovery path for an earlier manual copy that placed the Santali-only
        # page at frontend/views/voice.py. Preserve that exact page as santali_voice.py
        # and restore the last user-uploaded general voice page as voice.py, then
        # route Santali through it. This protects the application's expected entrypoint.
        current_voice_text = read_text(voice_path)
        recovered_santali_page = None
        voice_text_to_patch = current_voice_text
        has_santali_entry = bool(re.search(r"(?m)^def\s+show_santali_voice_page\s*\(", current_voice_text))
        has_generic_entry = bool(re.search(r"(?m)^def\s+show_voice_page\s*\(", current_voice_text))
        if has_santali_entry and not has_generic_entry:
            legacy_base = payload / "frontend/views/voice_legacy_base.py"
            if not legacy_base.is_file():
                raise ValueError(
                    "voice.py contains only show_santali_voice_page(); the safe recovery voice base is missing from this package."
                )
            recovered_santali_page = current_voice_text
            voice_text_to_patch = read_text(legacy_base)
            print("Detected Santali-only voice.py; will preserve it as santali_voice.py and restore the general voice entrypoint.")

        voice_new, voice_changed = patch_voice(voice_text_to_patch)
        const_new, side_new, const_changed, side_changed = patch_selector(
            read_text(constants_path), read_text(sidebar_path)
        )
        # A previously-installed Step 13 router is patched in place. If it is absent,
        # bootstrap from the known bundled ONNX router so this remains one install package.
        if router_path.is_file():
            router_original = read_text(router_path)
        else:
            bundled_router = payload / "backend/tribal_languages/santali_onnx_router.py"
            if not bundled_router.is_file():
                raise ValueError("Santali ONNX router is missing from both the project and package payload.")
            router_original = read_text(bundled_router)
        router_new, router_changed = patch_router(router_original)
        main_new, main_changed = patch_main(read_text(main_path))

        patch_items = [
            (chat_path, chat_new, chat_changed),
            (voice_path, voice_new, voice_changed),
            (constants_path, const_new, const_changed),
            (sidebar_path, side_new, side_changed),
            (router_path, router_new, router_changed),
            (main_path, main_new, main_changed),
        ]
        if recovered_santali_page is not None:
            santali_voice_path = project_root / "frontend/views/santali_voice.py"
            patch_items.append((santali_voice_path, recovered_santali_page, True))

        for path, updated, changed in patch_items:
            if changed and (not path.is_file() or updated != read_text(path)):
                changes.append((path, updated))

    except Exception as exc:
        print(f"ERROR: Integration validation failed before writing files: {type(exc).__name__}: {exc}")
        print("No code files have been modified.")
        return 3

    # Copy the new modules only after all text patches validated.
    for relative in [
        "frontend/api/santali_onnx_client.py",
        "frontend/api/santali_translation.py",
        "frontend/api/santali_chat_bridge.py",
        "frontend/api/santali_tts.py",
        "frontend/views/santali_voice.py",
        "backend/tribal_languages/santali_onnx_stt_service.py",
        "backend/tribal_languages/santali_translation_service.py",
        "backend/tribal_languages/santali_tts_service.py",
        "backend/tribal_languages/santali_language_router.py",
        "tests/test_santali_unified.py",
        "tests/test_santali_voice_source.py",
        "tests/test_santali_onnx_router.py",
    ]:
        source = payload / relative
        if not source.is_file():
            print(f"ERROR: Package file missing: {source}")
            return 4

    try:
        for path, updated in changes:
            if path.exists():
                backup = backup_once(path)
                print(f"Backup:  {backup.relative_to(project_root)}")
                action = "Updated"
            else:
                path.parent.mkdir(parents=True, exist_ok=True)
                action = "Added"
            path.write_text(updated, encoding="utf-8", newline="")
            print(f"{action}: {path.relative_to(project_root)}")
        module_relatives = [
            "frontend/api/santali_onnx_client.py",
            "frontend/api/santali_translation.py",
            "frontend/api/santali_chat_bridge.py",
            "frontend/api/santali_tts.py",
            "frontend/views/santali_voice.py",
            "backend/tribal_languages/santali_onnx_stt_service.py",
            "backend/tribal_languages/santali_translation_service.py",
            "backend/tribal_languages/santali_tts_service.py",
            "backend/tribal_languages/santali_language_router.py",
            "tests/test_santali_unified.py",
            "tests/test_santali_voice_source.py",
            "tests/test_santali_onnx_router.py",
        ]
        # In recovery mode, keep the user's exact Santali-only voice page from the
        # current voice.py; do not overwrite it with the bundled copy.
        if recovered_santali_page is not None:
            module_relatives = [r for r in module_relatives if r != "frontend/views/santali_voice.py"]
        for relative in module_relatives:
            destination = project_root / relative
            source = payload / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            if destination.exists() and read_text(destination) != read_text(source):
                backup_once(destination)
            if not destination.exists() or read_text(destination) != read_text(source):
                shutil.copy2(source, destination)
                print(f"Installed: {relative}")
        env_changed = update_env(project_root / ".env")
        if env_changed:
            print("Updated .env: TRIBAL_SANTALI_ONNX_STT_ENABLED=true (backup created).")
        dependency_changed = False
        for name in ("requirements.txt", "requirements-docker.txt", "requirements-docker-tribal-updated.txt"):
            dependency_changed = append_missing_dependencies(project_root / name) or dependency_changed
        if dependency_changed:
            print("Updated/normalized existing requirements file(s); backups created.")
    except Exception as exc:
        print(f"ERROR while applying the validated patch: {type(exc).__name__}: {exc}")
        print("Restore from the *.santali_unified.bak files if necessary.")
        return 5

    print("\nSantali unified integration installed.")
    print("- Main language selector: Santali (Ol Chiki), no per-session enable checkbox")
    print("- Typed chat: English or Ol Chiki question -> existing chatbot/RAG -> Santali answer")
    print("- Voice: English uses the existing English STT; Santali uses the Santali ONNX STT; both answer in Santali")
    print("- Voice replies also attempt Santali TTS; text answers remain available if TTS fails")
    print("- Existing non-Santali chat and voice paths are retained.")
    print("- First use downloads translation models and the small Santali TTS ONNX model; HF model conditions may be required.")
    print("- Santali ONNX STT router and client are included in this same package; no per-use experimental toggle is required.")
    print("- Existing requirements.txt is updated in place only if dependencies are missing; no new requirements file is created.")
    install_marker.parent.mkdir(parents=True, exist_ok=True)
    install_marker.write_text("installed\n", encoding="utf-8")
    # The payload is only a temporary installation staging tree, not a nested project.
    try:
        shutil.rmtree(payload)
        print("Removed temporary santali_unified_payload staging folder; all installed modules are in the existing project folders.")
    except OSError as exc:
        print(f"NOTE: Could not remove temporary staging folder automatically: {exc}")
    print("Next: run py_compile and unittest commands in README, then restart backend and Streamlit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
