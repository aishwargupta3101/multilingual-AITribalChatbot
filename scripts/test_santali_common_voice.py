"""Run a first Santali ASR smoke test against a local Common Voice dataset.

No dataset/audio is bundled. Extract Common Voice locally, then run:
    python scripts/test_santali_common_voice.py "C:\\path\\to\\extracted\\dataset"

It chooses a transcript/audio pair from test.tsv first, then validated.tsv.
It uses cached IndicConformer files only; no model weights are downloaded.
"""
from __future__ import annotations

import argparse
import csv
import os
import sys
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = "ai4bharat/indic-conformer-600m-multilingual"
LANGUAGE_CODE = "sat"


def find_tsv_and_clip(dataset_root: Path) -> tuple[Path, Path, str]:
    priorities = ("test.tsv", "validated.tsv", "dev.tsv", "train.tsv")
    tsv_files = list(dataset_root.rglob("*.tsv"))
    ranked: list[Path] = []
    for name in priorities:
        ranked.extend(sorted((p for p in tsv_files if p.name.lower() == name), key=str))
    for tsv_path in ranked:
        try:
            with tsv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle, delimiter="\t")
                if not reader.fieldnames:
                    continue
                for row in reader:
                    rel = (row.get("path") or row.get("filename") or "").strip()
                    sentence = (row.get("sentence") or row.get("text") or "").strip()
                    if not rel or not sentence:
                        continue
                    candidate = (tsv_path.parent / rel).resolve()
                    if not candidate.is_file():
                        # Some dataset bundles put TSV files above or beside the clips directory.
                        matches = list(dataset_root.rglob(Path(rel).name))
                        candidate = matches[0].resolve() if matches else candidate
                    if candidate.is_file():
                        return tsv_path, candidate, sentence
        except (OSError, csv.Error, UnicodeError):
            continue
    raise FileNotFoundError(
        "Could not find a TSV transcript row with an existing audio file. "
        "Confirm the archive is fully extracted and the TSV is alongside its clips/ directory."
    )


def char_error_rate(reference: str, hypothesis: str) -> float:
    # Plain Unicode code-point CER for rough smoke-test feedback; not a formal evaluation.
    ref, hyp = reference.replace(" ", ""), hypothesis.replace(" ", "")
    if not ref:
        return 0.0 if not hyp else 1.0
    previous = list(range(len(hyp) + 1))
    for i, rchar in enumerate(ref, start=1):
        current = [i]
        for j, hchar in enumerate(hyp, start=1):
            current.append(min(
                current[-1] + 1,          # insertion
                previous[j] + 1,           # deletion
                previous[j - 1] + (rchar != hchar),  # substitution
            ))
        previous = current
    return previous[-1] / len(ref)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dataset_dir", help="Path to the extracted Common Voice Santali dataset folder")
    parser.add_argument("--decoder", choices=("ctc", "rnnt"), default="ctc")
    parser.add_argument("--allow-low-ram", action="store_true",
                        help="Proceed if available RAM is below 5 GB (risk of heavy paging/OOM).")
    args = parser.parse_args()

    dataset_root = Path(args.dataset_dir).expanduser().resolve()
    if not dataset_root.is_dir():
        print(f"ERROR: dataset directory not found: {dataset_root}", file=sys.stderr)
        return 2

    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env", override=False)
    except ImportError:
        pass

    if os.getenv("TRIBAL_SANTALI_STT_HF_ACCESS_ACCEPTED", "").strip().lower() not in {"1", "true", "yes", "on"}:
        print("ERROR: set TRIBAL_SANTALI_STT_HF_ACCESS_ACCEPTED=true only if you personally accepted the model repository conditions.", file=sys.stderr)
        return 2

    try:
        import psutil
        available_gb = psutil.virtual_memory().available / (1024 ** 3)
    except Exception:
        available_gb = None

    if available_gb is not None:
        print(f"Currently available RAM: {available_gb:.2f} GB")
        if available_gb < 3.0:
            print("ERROR: less than 3 GB RAM is available; stopping before model load.", file=sys.stderr)
            return 3
        if available_gb < 5.0 and not args.allow_low_ram:
            print("ERROR: this 600M-parameter model may need more memory. Close memory-heavy apps and retry; only use --allow-low-ram if you accept OOM/paging risk.", file=sys.stderr)
            return 3

    try:
        tsv_path, audio_path, reference = find_tsv_and_clip(dataset_root)
    except Exception as exc:
        print(f"ERROR finding a reference audio item: {exc}", file=sys.stderr)
        return 2

    print(f"Selected manifest: {tsv_path}")
    print(f"Selected clip: {audio_path}")
    print(f"Reference transcript: {reference}")

    try:
        import torch
        import torchaudio
        from transformers import AutoModel
    except ImportError as exc:
        print(f"ERROR: required package missing: {exc.name}", file=sys.stderr)
        return 2

    torch.set_num_threads(2)
    load_kwargs = {
        "trust_remote_code": True,
        "local_files_only": True,
        "low_cpu_mem_usage": True,
    }
    token = os.getenv("HF_TOKEN", "").strip()
    if token:
        load_kwargs["token"] = token

    print(f"Loading cached model: {MODEL_ID}")
    print("No model weights will be downloaded by this script.")
    try:
        waveform, sample_rate = torchaudio.load(str(audio_path))
        if waveform.ndim == 1:
            waveform = waveform.unsqueeze(0)
        waveform = waveform.mean(dim=0, keepdim=True)
        target_rate = 16000
        if sample_rate != target_rate:
            resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=target_rate)
            waveform = resampler(waveform)
        waveform = waveform.to(dtype=torch.float32)

        model = AutoModel.from_pretrained(MODEL_ID, **load_kwargs)
        model.eval()
        with torch.inference_mode():
            result = model(waveform, LANGUAGE_CODE, args.decoder)
    except Exception as exc:
        print(f"ERROR during local transcription ({type(exc).__name__}): {exc}", file=sys.stderr)
        print("Inference was not enabled in FastAPI. Check model/runtime compatibility and available RAM.", file=sys.stderr)
        return 1

    if isinstance(result, (tuple, list)):
        result = result[0] if result else ""
    hypothesis = str(result).strip()
    print("\n--- SANTALI COMMON VOICE SMOKE TEST ---")
    print("Reference:", reference)
    print("Model output:", hypothesis or "<empty>")
    print(f"Approximate character error rate: {char_error_rate(reference, hypothesis):.3f}")
    print("Reminder: Common Voice transcripts are references for smoke testing, not a substitute for native-speaker quality review.")
    print("--- END ---")
    return 0 if hypothesis else 1


if __name__ == "__main__":
    raise SystemExit(main())
