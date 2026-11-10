"""Controlled local smoke test for AI4Bharat IndicConformer Santali ASR.

Run from project root:
    python scripts/test_santali_stt_local.py "C:\path\to\short_santali_audio.wav"

The script uses the already-cached model only; it does not download weights.
It does not enable the FastAPI endpoint or change project configuration.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=False)
except ImportError:
    pass

MODEL_ID = "ai4bharat/indic-conformer-600m-multilingual"
LANGUAGE_CODE = "sat"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run one local Santali STT smoke test.")
    parser.add_argument("audio_file", help="Path to a short, consented Santali audio file (WAV/FLAC/OGG supported by soundfile).")
    parser.add_argument("--decoder", choices=("ctc", "rnnt"), default="ctc")
    parser.add_argument(
        "--max-seconds", type=float, default=20.0,
        help="Use only the first N seconds for this initial smoke test (default: 20; use 0 for full clip).",
    )
    parser.add_argument(
        "--allow-low-ram", action="store_true",
        help="Proceed despite low available RAM. May cause heavy paging or an out-of-memory failure.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audio_path = Path(args.audio_file).expanduser().resolve()
    if not audio_path.is_file():
        print(f"ERROR: audio file not found: {audio_path}", file=sys.stderr)
        return 2

    if os.getenv("TRIBAL_SANTALI_STT_HF_ACCESS_ACCEPTED", "").strip().lower() not in {"1", "true", "yes", "on"}:
        print(
            "ERROR: set TRIBAL_SANTALI_STT_HF_ACCESS_ACCEPTED=true in .env only if you personally accepted the model repository conditions.",
            file=sys.stderr,
        )
        return 2

    try:
        import psutil
        available_gb = psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        available_gb = None

    if available_gb is not None:
        print(f"Currently available RAM: {available_gb:.2f} GB")
        if available_gb < 3.0:
            print(
                "ERROR: less than 3 GB RAM is currently available. Close memory-heavy apps and retry later.",
                file=sys.stderr,
            )
            return 3
        if available_gb < 5.0:
            print(
                "WARNING: this 600M-parameter model may exceed available RAM and cause paging or an out-of-memory failure.",
                file=sys.stderr,
            )
            if not args.allow_low_ram:
                print(
                    "For safety, the model was not loaded. Free more RAM and retry, or explicitly pass --allow-low-ram to accept the risk.",
                    file=sys.stderr,
                )
                return 3

    try:
        import numpy as np
        import soundfile as sf
        import torch
        from scipy.signal import resample_poly
        from transformers import AutoModel
        from math import gcd
    except ImportError as exc:
        print(f"ERROR: required package missing: {exc.name}", file=sys.stderr)
        return 2

    # This local test is intentionally CPU-only and low-thread-count to limit resource spikes.
    torch.set_num_threads(2)
    os.environ.setdefault("HF_HUB_OFFLINE", "1")

    try:
        audio, sample_rate = sf.read(str(audio_path), dtype="float32")
    except Exception as exc:
        print(f"ERROR: could not decode audio file: {exc}", file=sys.stderr)
        return 2

    if audio.size == 0:
        print("ERROR: the audio file contains no samples.", file=sys.stderr)
        return 2
    if audio.ndim > 1:
        audio = np.mean(audio, axis=1)

    if sample_rate != 16000:
        g = gcd(int(sample_rate), 16000)
        audio = resample_poly(audio, 16000 // g, int(sample_rate) // g).astype(np.float32)
        sample_rate = 16000

    duration = len(audio) / sample_rate
    if args.max_seconds > 0 and duration > args.max_seconds:
        audio = audio[: int(args.max_seconds * sample_rate)]
        print(f"Audio duration: {duration:.1f}s; using first {args.max_seconds:.1f}s for this smoke test.")
    else:
        print(f"Audio duration: {duration:.1f}s")

    audio = np.asarray(audio, dtype=np.float32)
    waveform = torch.from_numpy(audio).unsqueeze(0)

    token = os.getenv("HF_TOKEN", "").strip()
    load_kwargs = {
        "trust_remote_code": True,
        "local_files_only": True,
        "low_cpu_mem_usage": True,
    }
    if token:
        load_kwargs["token"] = token

    print(f"Loading cached model: {MODEL_ID}")
    print("No model weights will be downloaded by this script.")
    try:
        model = AutoModel.from_pretrained(MODEL_ID, **load_kwargs)
        model.eval()
        with torch.inference_mode():
            result = model(waveform, LANGUAGE_CODE, args.decoder)
    except Exception as exc:
        print(
            f"ERROR: local inference failed ({type(exc).__name__}). "
            "Check backend/model compatibility and the traceback below; inference was not enabled in FastAPI.",
            file=sys.stderr,
        )
        raise

    if isinstance(result, (list, tuple)):
        result = result[0] if result else ""
    text = str(result).strip()
    if not text:
        print("ERROR: model returned an empty transcription.", file=sys.stderr)
        return 1

    print("\n--- SANTALI STT RESULT (experimental; needs native-speaker review) ---")
    print(text)
    print("--- END RESULT ---")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
