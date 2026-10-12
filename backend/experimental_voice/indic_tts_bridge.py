
import os
import subprocess
import sys
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
WORKER = PROJECT_ROOT / "backend" / "experimental_voice" / "indic_tts_worker.py"
OUTPUT_DIR = Path(os.getenv(
    "MANIPURI_TTS_OUTPUT_DIR",
    str(PROJECT_ROOT / "experimental_outputs" / "manipuri_tts" / "unified")
))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_manipuri_tts(text: str, script: str = "bengali", speaker: str = "female"):
    if not WORKER.is_file():
        raise RuntimeError(f"Manipuri TTS worker not found: {WORKER}")

    output_path = OUTPUT_DIR / f"{uuid.uuid4().hex}.wav"
    result = subprocess.run(
        [sys.executable, str(WORKER), text, script, speaker, str(output_path)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=300,
    )
    if result.returncode != 0:
        detail = (result.stdout.strip() + "\n" + result.stderr.strip()).strip()
        raise RuntimeError(detail or "Manipuri TTS generation failed.")
    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError("Manipuri TTS did not create a valid audio file.")
    return output_path
