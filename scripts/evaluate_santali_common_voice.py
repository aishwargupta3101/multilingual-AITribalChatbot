"""Evaluate the cached Santali ONNX model over a small Common Voice test subset.

Run from the project root:
  python scripts/evaluate_santali_common_voice.py "C:\\path\\to\\extracted\\sat" --max-samples 10

This is a local evaluation utility; it does not enable or modify any API routes.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
import unicodedata
from pathlib import Path
from typing import Iterable


MODEL_ID = "OpenVoiceOS/ai4bharat-indicconformer-sat-onnx"


def normalise(text: str, *, keep_spaces: bool = True) -> str:
    text = unicodedata.normalize("NFC", str(text or ""))
    text = " ".join(text.split())
    if not keep_spaces:
        text = "".join(text.split())
    return text


def edit_distance(ref: str, hyp: str) -> int:
    if len(hyp) > len(ref):
        ref, hyp = hyp, ref
    previous = list(range(len(hyp) + 1))
    for i, rchar in enumerate(ref, start=1):
        current = [i]
        for j, hchar in enumerate(hyp, start=1):
            current.append(min(
                current[-1] + 1,       # insertion
                previous[j] + 1,       # deletion
                previous[j - 1] + (rchar != hchar),
            ))
        previous = current
    return previous[-1]


def word_edit_distance(ref: str, hyp: str) -> int:
    return edit_distance(normalise(ref).split(), normalise(hyp).split())


def cer_errors(ref: str, hyp: str, *, keep_spaces: bool) -> tuple[int, int]:
    r = normalise(ref, keep_spaces=keep_spaces)
    h = normalise(hyp, keep_spaces=keep_spaces)
    return edit_distance(r, h), len(r)


def find_test_tsv(root: Path) -> Path:
    candidates = [p for p in root.rglob("test.tsv") if p.is_file()]
    if not candidates:
        raise FileNotFoundError(
            f"No test.tsv found under {root}. Pass the extracted Santali folder containing test.tsv and clips/."
        )
    # Prefer manifest closest to the provided dataset root.
    return min(candidates, key=lambda p: len(p.parts))


def audio_for_row(root: Path, manifest: Path, row: dict[str, str]) -> Path | None:
    relative = (row.get("path") or row.get("filename") or "").strip()
    if not relative:
        return None
    rel = Path(relative)
    candidates = [
        manifest.parent / rel,
        manifest.parent / "clips" / rel.name,
        root / rel,
        root / "clips" / rel.name,
    ]
    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()
    # Fallback for Common Voice archives with a slightly different nesting.
    matches = [p for p in root.rglob(rel.name) if p.is_file()]
    return matches[0].resolve() if matches else None


def load_audio_mono_16k(path: Path):
    try:
        import av
        import numpy as np
    except ImportError as exc:
        raise RuntimeError(f"Missing dependency: {exc.name}. Install av and numpy.") from exc

    chunks = []
    with av.open(str(path)) as container:
        stream = next((s for s in container.streams if s.type == "audio"), None)
        if stream is None:
            raise ValueError("no audio stream")
        resampler = av.AudioResampler(format="fltp", layout="mono", rate=16000)
        for frame in container.decode(audio=stream.index):
            for out_frame in (resampler.resample(frame) or []):
                chunks.append(out_frame.to_ndarray().reshape(-1).astype(np.float32))
        for out_frame in (resampler.resample(None) or []):
            chunks.append(out_frame.to_ndarray().reshape(-1).astype(np.float32))
    if not chunks:
        raise ValueError("empty decoded audio")
    return np.concatenate(chunks).astype(np.float32, copy=False)


def main() -> int:
    parser = argparse.ArgumentParser(description="Evaluate Santali ONNX STT on a Common Voice test subset.")
    parser.add_argument("dataset_dir", help="Extracted Santali Common Voice folder containing test.tsv.")
    parser.add_argument("--max-samples", type=int, default=10, help="Number of valid samples, 1-50 (default 10).")
    parser.add_argument("--max-seconds", type=float, default=12.0, help="Clip audio to N seconds (default 12; 0 = full clip).")
    parser.add_argument("--output", default="", help="Optional output CSV path. Default: santali_onnx_eval_results.csv beside test.tsv.")
    args = parser.parse_args()

    if not 1 <= args.max_samples <= 50:
        parser.error("--max-samples must be between 1 and 50.")
    if args.max_seconds < 0:
        parser.error("--max-seconds cannot be negative.")

    root = Path(args.dataset_dir).expanduser().resolve()
    if not root.is_dir():
        print(f"ERROR: dataset directory not found: {root}", file=sys.stderr)
        return 2

    try:
        import psutil
        ram_gb = psutil.virtual_memory().available / (1024 ** 3)
        print(f"Currently available RAM: {ram_gb:.2f} GB")
        if ram_gb < 2.0:
            print("ERROR: less than 2 GB RAM is available; stopping before model load.", file=sys.stderr)
            return 3
    except ImportError:
        print("WARNING: psutil unavailable; cannot check available RAM.", file=sys.stderr)

    try:
        from dotenv import load_dotenv
        project_root = Path(__file__).resolve().parents[1]
        load_dotenv(project_root / ".env", override=False)
    except ImportError:
        pass

    try:
        import onnx_asr
    except ImportError as exc:
        print(f"ERROR: onnx-asr is missing: {exc.name}. Install `onnx-asr[cpu,hub]` in the active .venv.", file=sys.stderr)
        return 2

    try:
        manifest = find_test_tsv(root)
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    print(f"Manifest: {manifest}")
    print(f"Model: {MODEL_ID}")
    print("Using cached/unquantized ONNX with CPU provider; the API remains disabled.")

    output_path = Path(args.output).expanduser().resolve() if args.output else manifest.parent / "santali_onnx_eval_results.csv"
    records: list[dict[str, str]] = []
    total_cer_err = total_cer_chars = 0
    total_cer_nospace_err = total_cer_nospace_chars = 0
    total_wer_err = total_wer_words = 0

    try:
        model = onnx_asr.load_model(
            MODEL_ID,
            quantization=None,
            providers=["CPUExecutionProvider"],
        )
    except Exception as exc:
        print(f"ERROR: could not load ONNX model: {type(exc).__name__}: {exc}", file=sys.stderr)
        return 1

    used = 0
    seen_audio: set[str] = set()
    try:
        with manifest.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter="\t")
            for row in reader:
                reference = (row.get("sentence") or row.get("text") or "").strip()
                audio_path = audio_for_row(root, manifest, row)
                if not reference or audio_path is None or str(audio_path) in seen_audio:
                    continue
                seen_audio.add(str(audio_path))
                try:
                    audio = load_audio_mono_16k(audio_path)
                except Exception as exc:
                    print(f"Skipping undecodable clip {audio_path.name}: {exc}", file=sys.stderr)
                    continue

                if args.max_seconds > 0:
                    audio = audio[:int(args.max_seconds * 16000)]
                duration = len(audio) / 16000
                if duration <= 0:
                    continue

                try:
                    hypothesis = model.recognize(audio, sample_rate=16000)
                    if isinstance(hypothesis, (list, tuple)):
                        hypothesis = hypothesis[0] if hypothesis else ""
                    hypothesis = str(hypothesis).strip()
                except Exception as exc:
                    print(f"ERROR on {audio_path.name}: {type(exc).__name__}: {exc}", file=sys.stderr)
                    print("Stopping after first inference error; no API flags were changed.", file=sys.stderr)
                    return 1

                ce, cn = cer_errors(reference, hypothesis, keep_spaces=True)
                cns, nns = cer_errors(reference, hypothesis, keep_spaces=False)
                ref_words = normalise(reference).split()
                hyp_words = normalise(hypothesis).split()
                we = word_edit_distance(reference, hypothesis)
                total_cer_err += ce
                total_cer_chars += cn
                total_cer_nospace_err += cns
                total_cer_nospace_chars += nns
                total_wer_err += we
                total_wer_words += len(ref_words)
                records.append({
                    "sample_index": str(used + 1),
                    "audio_filename": audio_path.name,
                    "duration_seconds": f"{duration:.2f}",
                    "reference": reference,
                    "prediction": hypothesis,
                    "cer_with_spaces": f"{(ce / cn if cn else 0.0):.4f}",
                    "cer_without_spaces": f"{(cns / nns if nns else 0.0):.4f}",
                    "wer": f"{(we / len(ref_words) if ref_words else 0.0):.4f}",
                })
                used += 1
                print(f"[{used}/{args.max_samples}] {audio_path.name} | {duration:.2f}s")
                if used >= args.max_samples:
                    break
    finally:
        # Release references before exit, especially useful on RAM-constrained systems.
        try:
            del model
        except UnboundLocalError:
            pass

    if not records:
        print("ERROR: no usable test samples were evaluated.", file=sys.stderr)
        return 1

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0].keys()))
        writer.writeheader()
        writer.writerows(records)

    print("\n--- SANTALI STT BATCH SUMMARY ---")
    print(f"Samples evaluated: {used}")
    print(f"Aggregate CER (with spaces): {total_cer_err / total_cer_chars if total_cer_chars else 0.0:.4f}")
    print(f"Aggregate CER (without spaces): {total_cer_nospace_err / total_cer_nospace_chars if total_cer_nospace_chars else 0.0:.4f}")
    print(f"Aggregate WER: {total_wer_err / total_wer_words if total_wer_words else 0.0:.4f}")
    print(f"Local results CSV: {output_path}")
    print("Interpretation: small-subset evaluation only; not a native-speaker quality certification.")
    print("Keep TRIBAL_SANTALI_ONNX_STT_ENABLED=false pending broader review.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
