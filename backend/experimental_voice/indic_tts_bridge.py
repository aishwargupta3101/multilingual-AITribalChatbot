import subprocess
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

INDIC_PYTHON = PROJECT_ROOT / ".venv_indic_tts" / "Scripts" / "python.exe"
WORKER = PROJECT_ROOT / "backend" / "experimental_voice" / "indic_tts_worker.py"

OUTPUT_DIR = PROJECT_ROOT / "experimental_outputs" / "manipuri_tts" / "unified"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_manipuri_tts(
    text: str,
    script: str = "bengali",
    speaker: str = "female"
):
    if not INDIC_PYTHON.exists():
        raise RuntimeError(
            f"AI4Bharat Python environment not found: {INDIC_PYTHON}"
        )

    if not WORKER.exists():
        raise RuntimeError(
            f"AI4Bharat worker not found: {WORKER}"
        )

    output_path = OUTPUT_DIR / f"{uuid.uuid4().hex}.wav"

    result = subprocess.run(
        [
            str(INDIC_PYTHON),
            str(WORKER),
            text,
            script,
            speaker,
            str(output_path),
        ],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )

    if result.returncode != 0:
        raise RuntimeError(
            result.stdout.strip()
            or result.stderr.strip()
            or "AI4Bharat TTS failed."
        )

    if not output_path.exists():
        raise RuntimeError("AI4Bharat did not create the audio file.")

    return output_path