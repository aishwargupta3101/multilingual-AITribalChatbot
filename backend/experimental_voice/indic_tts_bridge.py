
import os
import uuid
from pathlib import Path
from backend.experimental_voice import indic_tts_worker

PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(os.getenv(
    "MANIPURI_TTS_OUTPUT_DIR",
    str(PROJECT_ROOT / "experimental_outputs" / "manipuri_tts" / "unified")
))
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_manipuri_tts(text: str, script: str = "bengali", speaker: str = "female"):
    if not text or not text.strip():
        raise ValueError("Manipuri TTS text is empty.")

    output_path = OUTPUT_DIR / f"{uuid.uuid4().hex}.wav"
    indic_tts_worker.generate(
        text=text,
        script=script,
        speaker=speaker,
        output_path=str(output_path),
    )

    if not output_path.is_file() or output_path.stat().st_size == 0:
        raise RuntimeError("Manipuri TTS did not create a valid audio file.")

    return output_path
