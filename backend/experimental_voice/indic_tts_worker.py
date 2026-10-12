
import json
import os
import sys
import tempfile
import threading
import wave
from pathlib import Path
import numpy as np

_SYNTHESIZER = None
_SYNTHESIZER_LOCK = threading.Lock()
_GENERATION_LOCK = threading.Lock()

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

FASTPITCH_MODEL = os.getenv("MANIPURI_FASTPITCH_MODEL", "").strip()
FASTPITCH_CONFIG = os.getenv("MANIPURI_FASTPITCH_CONFIG", "").strip()
SPEAKERS_FILE = os.getenv("MANIPURI_SPEAKERS_FILE", "").strip()
HIFIGAN_MODEL = os.getenv("MANIPURI_HIFIGAN_MODEL", "").strip()
HIFIGAN_CONFIG = os.getenv("MANIPURI_HIFIGAN_CONFIG", "").strip()


def _require_model_files():
    global FASTPITCH_MODEL, FASTPITCH_CONFIG, SPEAKERS_FILE
    global HIFIGAN_MODEL, HIFIGAN_CONFIG

    configured = {
        "MANIPURI_FASTPITCH_MODEL": FASTPITCH_MODEL,
        "MANIPURI_FASTPITCH_CONFIG": FASTPITCH_CONFIG,
        "MANIPURI_SPEAKERS_FILE": SPEAKERS_FILE,
        "MANIPURI_HIFIGAN_MODEL": HIFIGAN_MODEL,
        "MANIPURI_HIFIGAN_CONFIG": HIFIGAN_CONFIG,
    }

    if all(value and Path(value).is_file() for value in configured.values()):
        return

    repo_id = os.getenv("HF_REPO_ID", "").strip()
    token = os.getenv("HF_TOKEN", "").strip()

    if not repo_id or not token:
        missing = [
            name for name, value in configured.items()
            if not value or not Path(value).is_file()
        ]
        raise RuntimeError(
            "Manipuri TTS model files are unavailable. Configure valid model "
            "paths or HF_REPO_ID and HF_TOKEN. Missing: "
            + ", ".join(missing)
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

    resolved = {
        "MANIPURI_FASTPITCH_MODEL": FASTPITCH_MODEL,
        "MANIPURI_FASTPITCH_CONFIG": FASTPITCH_CONFIG,
        "MANIPURI_SPEAKERS_FILE": SPEAKERS_FILE,
        "MANIPURI_HIFIGAN_MODEL": HIFIGAN_MODEL,
        "MANIPURI_HIFIGAN_CONFIG": HIFIGAN_CONFIG,
    }

    missing = [
        f"{name}={value}"
        for name, value in resolved.items()
        if not value or not Path(value).is_file()
    ]

    if missing:
        raise RuntimeError(
            "Manipuri TTS model download did not produce all required files: "
            + "; ".join(missing)
        )


def _make_runtime_fastpitch_config():
    config_path = Path(FASTPITCH_CONFIG).resolve()
    speakers_path = str(Path(SPEAKERS_FILE).resolve())

    with config_path.open("r", encoding="utf-8") as file:
        config = json.load(file)

    # Replace stale training-machine paths with the actual downloaded file.
    config["speakers_file"] = speakers_path

    model_args = config.get("model_args")
    if isinstance(model_args, dict):
        model_args["speakers_file"] = speakers_path

    # Keep the original Hugging Face config unchanged.
    runtime_dir = Path(tempfile.gettempdir()) / "manipuri_tts_runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    runtime_config = runtime_dir / f"fastpitch-{os.getpid()}-config.json"
    temporary_config = runtime_config.with_suffix(".tmp")

    with temporary_config.open("w", encoding="utf-8") as file:
        json.dump(config, file, ensure_ascii=False)

    temporary_config.replace(runtime_config)
    return str(runtime_config)


def get_synthesizer():
    global _SYNTHESIZER

    if _SYNTHESIZER is None:
        with _SYNTHESIZER_LOCK:
            if _SYNTHESIZER is None:
                _require_model_files()
                from TTS.utils.synthesizer import Synthesizer

                runtime_config = _make_runtime_fastpitch_config()

                _SYNTHESIZER = Synthesizer(
                    tts_checkpoint=FASTPITCH_MODEL,
                    tts_config_path=runtime_config,
                    tts_speakers_file=SPEAKERS_FILE,
                    vocoder_checkpoint=HIFIGAN_MODEL,
                    vocoder_config=HIFIGAN_CONFIG,
                    use_cuda=False,
                )

    return _SYNTHESIZER


def generate(text: str, script: str, speaker: str, output_path: str):
    if not text or not text.strip():
        raise ValueError("Manipuri TTS text is empty.")

    if script == "meitei_mayek":
        from backend.translation.meitei_script_converter import (
            convert_meitei_to_bengali,
        )
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

    with wave.open(str(output), "wb") as file:
        file.setnchannels(1)
        file.setsampwidth(2)
        file.setframerate(synthesizer.tts_model.ap.sample_rate)
        file.writeframes(audio.tobytes())
