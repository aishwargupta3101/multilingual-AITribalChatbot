"""Low-memory Santali STT smoke test using INT8 ONNX.

Usage from project root:
  python scripts/test_santali_onnx_int8.py "C:\\path\\to\\Common Voice\\sat"

This does not enable any FastAPI routes. The first run downloads the ONNX
model variant from Hugging Face; subsequent runs reuse the Hugging Face cache.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path

MODEL_ID = "OpenVoiceOS/ai4bharat-indicconformer-sat-onnx"


def find_item(root: Path) -> tuple[Path, Path, str]:
    priority = ("test.tsv", "validated.tsv", "dev.tsv", "train.tsv")
    all_tsv = list(root.rglob("*.tsv"))
    for filename in priority:
        for tsv in (p for p in all_tsv if p.name.lower() == filename):
            try:
                with tsv.open("r", encoding="utf-8-sig", newline="") as handle:
                    reader = csv.DictReader(handle, delimiter="\t")
                    for row in reader:
                        rel = (row.get("path") or row.get("filename") or "").strip()
                        sentence = (row.get("sentence") or row.get("text") or "").strip()
                        if not rel or not sentence:
                            continue
                        rel_path = Path(rel)
                        candidates = [
                            tsv.parent / rel_path,
                            tsv.parent / "clips" / rel_path.name,
                            root / rel_path,
                            root / "clips" / rel_path.name,
                        ]
                        audio_path = next((p.resolve() for p in candidates if p.is_file()), None)
                        if audio_path is None:
                            # Archive layout varies slightly across Common Voice releases.
                            audio_path = next(
                                (p.resolve() for p in root.rglob(rel_path.name) if p.is_file()),
                                None,
                            )
                        if audio_path is not None:
                            return tsv, audio_path, sentence
            except (OSError, csv.Error, UnicodeError):
                continue
    raise FileNotFoundError(
        "Could not find a transcript row with a matching audio file. "
        "Pass the extracted dataset folder that contains test.tsv/validated.tsv and clips/."
    )


def decode_audio_mono_16k(path: Path):
    try:
        import av
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(
            f"Missing dependency '{exc.name}'. Install the optional dependencies from "
            "requirements-santali-onnx.txt."
        ) from exc

    chunks = []
    with av.open(str(path)) as container:
        stream = next((s for s in container.streams if s.type == "audio"), None)
        if stream is None:
            raise RuntimeError("The selected Common Voice clip contains no audio stream.")
        resampler = av.AudioResampler(format="fltp", layout="mono", rate=16000)
        for frame in container.decode(audio=stream.index):
            for converted in (resampler.resample(frame) or []):
                chunks.append(converted.to_ndarray().reshape(-1).astype(np.float32))
        for converted in (resampler.resample(None) or []):
            chunks.append(converted.to_ndarray().reshape(-1).astype(np.float32))

    if not chunks:
        raise RuntimeError("Audio decoding produced no samples.")
    return np.concatenate(chunks), 16000


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one Santali STT smoke test using quantized ONNX.")
    parser.add_argument("dataset_dir", help="Extracted Common Voice Santali folder (contains test.tsv and clips/).")
    parser.add_argument("--max-seconds", type=float, default=12.0, help="Use only first N audio seconds (default 12).")
    parser.add_argument("--quantization", choices=("int8", "fp32"), default="fp32",
                        help="Use unquantized FP32 by default because CPU runtime rejected the signed INT8 ConvInteger graph.")
    args = parser.parse_args()

    root = Path(args.dataset_dir).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: dataset directory not found: {root}", file=sys.stderr)
        return 2

    try:
        from dotenv import load_dotenv
        project_root = Path(__file__).resolve().parents[1]
        load_dotenv(project_root / ".env", override=False)
    except ImportError:
        pass

    try:
        import psutil
        available_gb = psutil.virtual_memory().available / (1024 ** 3)
        print(f"Currently available RAM: {available_gb:.2f} GB")
        if available_gb < 2.0:
            print("ERROR: less than 2 GB RAM available. Close applications before loading the ONNX model.", file=sys.stderr)
            return 3
        if available_gb < 3.0:
            print("WARNING: memory is tight; INT8 ONNX should reduce weight memory, but loading may still fail.", file=sys.stderr)
    except ImportError:
        print("RAM check unavailable (psutil missing); continuing with caution.", file=sys.stderr)

    try:
        tsv, clip, reference = find_item(root)
        audio, sample_rate = decode_audio_mono_16k(clip)
    except Exception as exc:
        print(f"ERROR preparing sample: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 2

    max_samples = int(max(0, args.max_seconds) * sample_rate)
    if max_samples and len(audio) > max_samples:
        audio = audio[:max_samples]
    print(f"Manifest: {tsv}")
    print(f"Audio sample: {clip}")
    print(f"Duration used: {len(audio) / sample_rate:.2f}s")
    print(f"Reference transcript: {reference}")

    try:
        import onnx_asr
    except ImportError:
        print(
            "ERROR: onnx-asr is not installed. From the active .venv, run:\n"
            "  python -m pip install \"onnx-asr[cpu,hub]\"",
            file=sys.stderr,
        )
        return 2

    # onnx-asr uses quantization=None for the full-precision model; "fp32" is not a quantization label.
    quantization = "int8" if args.quantization == "int8" else None
    label = "INT8" if quantization == "int8" else "unquantized FP32"
    print(f"Loading {MODEL_ID} with {label} ONNX on CPU.")
    print("First run may download the FP32 ONNX data file. It will not load the 600M PyTorch model.")
    try:
        model = onnx_asr.load_model(
            MODEL_ID,
            quantization=quantization,
            providers=["CPUExecutionProvider"],
        )
        prediction = model.recognize(audio, sample_rate=sample_rate)
    except Exception as exc:
        print(f"ERROR: ONNX inference failed ({type(exc).__name__}): {exc}", file=sys.stderr)
        print("No FastAPI inference flags or existing project routes were changed.", file=sys.stderr)
        return 1

    if isinstance(prediction, (list, tuple)):
        prediction = prediction[0] if prediction else ""
    prediction = str(prediction).strip()
    print("\n--- SANTALI INT8 ONNX SMOKE TEST ---")
    print("Reference:", reference)
    print("Prediction:", prediction or "<empty>")
    print("--- END ---")
    print("This is one technical sample, not a formal accuracy result; keep Santali STT disabled pending broader evaluation.")
    return 0 if prediction else 1


if __name__ == "__main__":
    raise SystemExit(main())
