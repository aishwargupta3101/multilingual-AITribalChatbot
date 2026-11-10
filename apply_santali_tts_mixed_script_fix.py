from __future__ import annotations

from datetime import datetime
from pathlib import Path
import py_compile
import shutil
import sys

TARGET = Path("backend/tribal_languages/santali_tts_service.py")
HELPER = '''def _prepare_santali_tts_input(text: str) -> str:
    """Prepare audio-only text for the Ol Chiki Santali phonemizer.

    The displayed chatbot answer is not modified. Markdown delimiters and
    characters from unsupported writing systems are removed only from the
    text sent to this Santali-only TTS model.
    """
    import re
    import unicodedata

    source = str(text or "").replace("\\r\\n", "\\n").replace("\\r", "\\n")
    # Remove structural Markdown before phonemization.
    source = re.sub(r"(?m)^\\s{0,3}#{1,6}\\s*", "", source)
    source = re.sub(r"(?m)^\\s*(?:[-*+]\\s+|\\d+[.)]\\s+)", "", source)
    source = re.sub(r"\\*\\*|__|[*`~]", "", source)

    # The voice model is trained for Ol Chiki. Keep Ol Chiki, ASCII words
    # (e.g. AI), whitespace, and basic punctuation. Replace other scripts
    # (for example Bengali, Odia, or Arabic fragments) with spaces so their
    # unsupported marks cannot crash phonemization.
    allowed_ascii_punctuation = set(".,!?;:'\\\"()[]{}-/%&+")
    output = []
    removed = 0
    for char in source:
        codepoint = ord(char)
        is_olchiki = 0x1C50 <= codepoint <= 0x1C7F
        is_ascii_text = char.isascii() and (
            char.isalnum() or char.isspace() or char in allowed_ascii_punctuation
        )
        if is_olchiki or is_ascii_text:
            output.append(char)
        elif char.isspace():
            output.append(" ")
        else:
            output.append(" ")
            removed += 1

    prepared = re.sub(r"\\s+", " ", "".join(output)).strip()
    if removed:
        import logging
        logging.getLogger(__name__).warning(
            "Santali TTS omitted %d unsupported-script/formatting character(s) from audio input; displayed answer is unchanged.",
            removed,
        )

    has_olchiki_letter = any(
        0x1C50 <= ord(char) <= 0x1C7F
        and unicodedata.category(char).startswith("L")
        for char in prepared
    )
    if not prepared or not has_olchiki_letter:
        raise ValueError(
            "Santali speech needs Ol Chiki text. No supported Ol Chiki text remained after removing unsupported characters."
        )
    return prepared


'''


def main() -> int:
    if not TARGET.is_file():
        print(f"ERROR: Run this installer from your project root. Missing: {TARGET}")
        return 2

    source = TARGET.read_text(encoding="utf-8-sig")
    call_old = "tokens = phonemizer.santali_to_phonemes(clean)"
    call_new = "tokens = phonemizer.santali_to_phonemes(tts_text)"

    if "def _prepare_santali_tts_input(" in source:
        # Idempotent recovery if the helper is already present but wiring isn't.
        if call_old in source:
            source = source.replace(call_old, "tts_text = _prepare_santali_tts_input(clean)\n    tokens = phonemizer.santali_to_phonemes(tts_text)", 1)
        elif call_new in source and "tts_text = _prepare_santali_tts_input(clean)" in source:
            print("INFO: Santali TTS mixed-script guard is already installed.")
            try:
                py_compile.compile(str(TARGET), doraise=True)
            except py_compile.PyCompileError as exc:
                print(f"ERROR: Existing service failed syntax check: {exc}")
                return 3
            return 0
        else:
            print("ERROR: The TTS helper exists, but the expected phonemizer call was not found. No file changed.")
            return 4
    else:
        if source.count(call_old) != 1:
            print("ERROR: Could not uniquely locate the Santali phonemizer call. No file changed.")
            return 4
        marker = "def synthesize_santali_wav(text: str) -> bytes:\n"
        if source.count(marker) != 1:
            print("ERROR: Could not locate the TTS function. No file changed.")
            return 4
        source = source.replace(marker, HELPER + marker, 1)
        source = source.replace(call_old, "tts_text = _prepare_santali_tts_input(clean)\n    tokens = phonemizer.santali_to_phonemes(tts_text)", 1)

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = TARGET.with_name(f"{TARGET.name}.pre_mixed_script_fix_{stamp}.bak")
    shutil.copy2(TARGET, backup)
    TARGET.write_text(source, encoding="utf-8", newline="\n")
    try:
        py_compile.compile(str(TARGET), doraise=True)
    except py_compile.PyCompileError as exc:
        shutil.copy2(backup, TARGET)
        print(f"ERROR: Syntax check failed; restored original file. Details: {exc}")
        return 5

    print("SUCCESS: Santali TTS mixed-script guard applied and syntax-checked.")
    print(f"Updated: {TARGET}")
    print(f"Backup:  {backup}")
    print("Only audio input is cleaned; displayed chat text and all other language paths remain unchanged.")
    print("Restart FastAPI/backend before testing the Speak Santali answer button.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
