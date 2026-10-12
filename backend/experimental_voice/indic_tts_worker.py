import os
import sys
import wave
from pathlib import Path

import numpy as np

sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Configure these as Render environment variables to paths where the model files
# are actually present. Windows paths will not work in the Linux container.
FASTPITCH_MODEL = os.getenv("MANIPURI_FASTPITCH_MODEL", "")
FASTPITCH_CONFIG = os.getenv("MANIPURI_FASTPITCH_CONFIG", "")
SPEAKERS_FILE = os.getenv("MANIPURI_SPEAKERS_FILE", "")
HIFIGAN_MODEL = os.getenv("MANIPURI_HIFIGAN_MODEL", "")
HIFIGAN_CONFIG = os.getenv("MANIPURI_HIFIGAN_CONFIG", "")


def _require_model_files():
    paths = {
        "MANIPURI_FASTPITCH_MODEL": FASTPITCH_MODEL,
        "MANIPURI_FASTPITCH_CONFIG": FASTPITCH_CONFIG,
        "MANIPURI_SPEAKERS_FILE": SPEAKERS_FILE,
        "MANIPURI_HIFIGAN_MODEL": HIFIGAN_MODEL,
        "MANIPURI_HIFIGAN_CONFIG": HIFIGAN_CONFIG,
    }
    missing = [name for name, value in paths.items() if not value]
    if missing:
        raise RuntimeError(
            "Manipuri TTS model paths are not configured: " + ", ".join(missing)
        )
    missing_files = [f"{name}={value}" for name, value in paths.items()
                     if not Path(value).is_file()]
    if missing_files:
        raise RuntimeError(
            "Manipuri TTS model files are missing in this environment: "
            + "; ".join(missing_files)
        )


def generate(text: str, script: str, speaker: str, output_path: str):
    _require_model_files()

    if script == "meitei_mayek":
        # Reverse conversion requires the separately installed/provided
        # mtei2bangla dependency. Do not silently synthesize the wrong script.
        from backend.translation.meitei_script_converter import convert_meitei_to_bengali
        text = convert_meitei_to_bengali(text)

    text = text.replace("।", "").strip()
    if not text:
        raise ValueError("Text is empty after script conversion.")

    try:
        from TTS.utils.synthesizer import Synthesizer
    except ImportError as exc:
        raise RuntimeError(
            "The Coqui TTS package is not installed in this Python environment."
        ) from exc

    synthesizer = Synthesizer(
        tts_checkpoint=FASTPITCH_MODEL,
        tts_config_path=FASTPITCH_CONFIG,
        tts_speakers_file=SPEAKERS_FILE,
        vocoder_checkpoint=HIFIGAN_MODEL,
        vocoder_config=HIFIGAN_CONFIG,
        use_cuda=False,
    )
    wav = synthesizer.tts(text=text, speaker_name=speaker)
    audio = np.asarray(wav, dtype=np.float32)
    if audio.size == 0:
        raise RuntimeError("TTS returned empty audio.")
    audio = np.clip(audio, -1.0, 1.0)
    audio = (audio * 32767).astype(np.int16)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(synthesizer.tts_model.ap.sample_rate)
        wf.writeframes(audio.tobytes())


if __name__ == "__main__":
    if len(sys.argv) != 5:
        print("Usage: python indic_tts_worker.py <text> <script> <speaker> <output>")
        sys.exit(1)
    try:
        generate(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
        print("SUCCESS")
    except Exception as error:
        print(f"ERROR:{type(error).__name__}: {error}", file=sys.stderr)
        sys.exit(1)
