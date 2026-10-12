import os
import sys
import wave
from pathlib import Path

import numpy as np
import threading

_SYNTHESIZER = None
_SYNTHESIZER_LOCK = threading.Lock()
_GENERATION_LOCK = threading.Lock()
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
    global FASTPITCH_MODEL, FASTPITCH_CONFIG, SPEAKERS_FILE
    global HIFIGAN_MODEL, HIFIGAN_CONFIG

    paths = {
        "MANIPURI_FASTPITCH_MODEL": FASTPITCH_MODEL,
        "MANIPURI_FASTPITCH_CONFIG": FASTPITCH_CONFIG,
        "MANIPURI_SPEAKERS_FILE": SPEAKERS_FILE,
        "MANIPURI_HIFIGAN_MODEL": HIFIGAN_MODEL,
        "MANIPURI_HIFIGAN_CONFIG": HIFIGAN_CONFIG,
    }
    if all(value and Path(value).is_file() for value in paths.values()):
        return

    repo_id = os.getenv("HF_REPO_ID", "").strip()
    token = os.getenv("HF_TOKEN", "").strip()
    if not repo_id or not token:
        missing = [name for name, value in paths.items()
                   if not value or not Path(value).is_file()]
        raise RuntimeError(
            "Manipuri TTS model files are unavailable and HF_REPO_ID/HF_TOKEN "
            "are not configured. Missing: " + ", ".join(missing)
        )

    try:
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        raise RuntimeError(
            "huggingface_hub is required to download the private Manipuri TTS models."
        ) from exc

    model_dir = PROJECT_ROOT / "manipuri_tts_models"
    files = {
        "FASTPITCH_MODEL": "fastpitch/best_model.pth",
        "FASTPITCH_CONFIG": "fastpitch/config.json",
        "SPEAKERS_FILE": "fastpitch/speakers.pth",
        "HIFIGAN_MODEL": "hifigan/best_model.pth",
        "HIFIGAN_CONFIG": "hifigan/config.json",
    }
    downloaded = {}
    for key, filename in files.items():
        downloaded[key] = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            token=token,
            repo_type="model",
            local_dir=str(model_dir),
        )

    FASTPITCH_MODEL = downloaded["FASTPITCH_MODEL"]
    FASTPITCH_CONFIG = downloaded["FASTPITCH_CONFIG"]
    SPEAKERS_FILE = downloaded["SPEAKERS_FILE"]
    HIFIGAN_MODEL = downloaded["HIFIGAN_MODEL"]
    HIFIGAN_CONFIG = downloaded["HIFIGAN_CONFIG"]

    paths = {
        "MANIPURI_FASTPITCH_MODEL": FASTPITCH_MODEL,
        "MANIPURI_FASTPITCH_CONFIG": FASTPITCH_CONFIG,
        "MANIPURI_SPEAKERS_FILE": SPEAKERS_FILE,
        "MANIPURI_HIFIGAN_MODEL": HIFIGAN_MODEL,
        "MANIPURI_HIFIGAN_CONFIG": HIFIGAN_CONFIG,
    }
    missing_files = [f"{name}={value}" for name, value in paths.items()
                     if not Path(value).is_file()]
    if missing_files:
        raise RuntimeError(
            "Manipuri TTS model download did not produce all required files: "
            + "; ".join(missing_files)
        )
def get_synthesizer():
    global _SYNTHESIZER

    if _SYNTHESIZER is None:
        with _SYNTHESIZER_LOCK:
            if _SYNTHESIZER is None:
                _require_model_files()
                from TTS.utils.synthesizer import Synthesizer

                _SYNTHESIZER = Synthesizer(
                    tts_checkpoint=FASTPITCH_MODEL,
                    tts_config_path=FASTPITCH_CONFIG,
                    tts_speakers_file=SPEAKERS_FILE,
                    vocoder_checkpoint=HIFIGAN_MODEL,
                    vocoder_config=HIFIGAN_CONFIG,
                    use_cuda=False,
                )

    return _SYNTHESIZER



def generate(text: str, script: str, speaker: str, output_path: str):
    if script == "meitei_mayek":
        from backend.translation.meitei_script_converter import convert_meitei_to_bengali
        text = convert_meitei_to_bengali(text)

    text = text.replace("।", "").strip()
    if not text:
        raise ValueError("Text is empty after script conversion.")

    synthesizer = get_synthesizer()

    with _GENERATION_LOCK:
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
