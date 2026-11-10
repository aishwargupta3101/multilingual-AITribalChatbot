#!/usr/bin/env python3
"""Evaluate one Santali audio clip against its Common Voice TSV reference.

This script sends audio only to the configured API base URL (defaults to localhost),
looks up the matching filename in TSV metadata under --dataset-root, and reports
character and word error rates. It does not change application configuration.
"""
from __future__ import annotations

import argparse
import csv
import json
import mimetypes
import sys
import unicodedata
from pathlib import Path
from typing import Iterable

import requests

DEFAULT_ENDPOINT_PATH = "/api/v1/tribal-languages/santali-onnx/stt"


def levenshtein_distance(left: list[str], right: list[str]) -> int:
    """Calculate edit distance with O(min(n, m)) memory."""
    if len(left) < len(right):
        left, right = right, left
    if not right:
        return len(left)
    previous = list(range(len(right) + 1))
    for i, left_item in enumerate(left, start=1):
        current = [i]
        for j, right_item in enumerate(right, start=1):
            current.append(min(
                current[j - 1] + 1,
                previous[j] + 1,
                previous[j - 1] + (left_item != right_item),
            ))
        previous = current
    return previous[-1]


def normalize_text(text: str) -> str:
    """Normalize Unicode equivalence while preserving meaningful spaces."""
    return unicodedata.normalize("NFC", text or "").strip()


def calculate_metrics(reference: str, prediction: str) -> dict[str, float | int]:
    reference = normalize_text(reference)
    prediction = normalize_text(prediction)
    ref_chars = list(reference)
    pred_chars = list(prediction)
    ref_chars_no_space = [ch for ch in ref_chars if not ch.isspace()]
    pred_chars_no_space = [ch for ch in pred_chars if not ch.isspace()]
    ref_words = reference.split()
    pred_words = prediction.split()

    char_edits = levenshtein_distance(ref_chars, pred_chars)
    char_edits_no_space = levenshtein_distance(ref_chars_no_space, pred_chars_no_space)
    word_edits = levenshtein_distance(ref_words, pred_words)

    return {
        "cer_with_spaces": char_edits / max(1, len(ref_chars)),
        "cer_without_spaces": char_edits_no_space / max(1, len(ref_chars_no_space)),
        "wer": word_edits / max(1, len(ref_words)),
        "char_edits_with_spaces": char_edits,
        "char_edits_without_spaces": char_edits_no_space,
        "word_edits": word_edits,
        "reference_character_count": len(ref_chars),
        "reference_character_count_without_spaces": len(ref_chars_no_space),
        "reference_word_count": len(ref_words),
        "exact_match": reference == prediction,
        "spacing_only_match": "".join(ref_chars_no_space) == "".join(pred_chars_no_space),
    }


def find_reference(dataset_root: Path, audio_name: str) -> tuple[str | None, list[Path]]:
    """Find matching clip basename in Common Voice TSV files."""
    matches: list[tuple[str, Path]] = []
    for tsv_path in dataset_root.rglob("*.tsv"):
        try:
            with tsv_path.open("r", encoding="utf-8-sig", newline="") as handle:
                reader = csv.DictReader(handle, delimiter="\t")
                if not reader.fieldnames or "path" not in reader.fieldnames or "sentence" not in reader.fieldnames:
                    continue
                for row in reader:
                    if Path(row.get("path", "")).name.casefold() == audio_name.casefold():
                        matches.append((normalize_text(row.get("sentence", "")), tsv_path))
        except (OSError, UnicodeError, csv.Error) as exc:
            print(f"Warning: skipped {tsv_path}: {exc}", file=sys.stderr)

    references = {sentence for sentence, _ in matches if sentence}
    source_files = sorted({path for _, path in matches})
    if len(references) > 1:
        raise ValueError(
            f"Found conflicting reference sentences for {audio_name}: "
            + "; ".join(str(x) for x in source_files)
        )
    return (next(iter(references)) if references else None), source_files


def transcribe(audio_path: Path, api_base_url: str, endpoint_path: str, timeout: int) -> dict:
    url = api_base_url.rstrip("/") + "/" + endpoint_path.lstrip("/")
    mime_type = mimetypes.guess_type(audio_path.name)[0] or "application/octet-stream"
    try:
        with audio_path.open("rb") as audio_handle:
            response = requests.post(
                url,
                files={"audio": (audio_path.name, audio_handle, mime_type)},
                timeout=timeout,
            )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Could not call local Santali STT endpoint {url}: {exc}. "
            "Check that the backend is running and the experimental endpoint is enabled."
        ) from exc

    if not response.ok:
        detail = response.text[:1000]
        raise RuntimeError(f"STT endpoint returned HTTP {response.status_code}: {detail}")
    try:
        payload = response.json()
    except ValueError as exc:
        raise RuntimeError("STT endpoint returned a non-JSON response.") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("STT endpoint returned an unexpected response format.")
    if payload.get("success") is False:
        raise RuntimeError(str(payload.get("error") or "STT endpoint reported failure."))
    text = payload.get("text") or payload.get("transcription") or payload.get("transcript")
    if not isinstance(text, str) or not text.strip():
        raise RuntimeError(f"No transcription text found in API response: {payload}")
    return {"text": normalize_text(text), "payload": payload, "url": url}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio", type=Path, help="Path to one Santali audio file")
    parser.add_argument(
        "--dataset-root", type=Path, required=True,
        help="Extracted Common Voice root containing one or more TSV files (for example the sat folder)",
    )
    parser.add_argument("--api-base-url", default="http://127.0.0.1:8000", help="Local backend base URL")
    parser.add_argument("--endpoint-path", default=DEFAULT_ENDPOINT_PATH, help="STT route path")
    parser.add_argument("--timeout", type=int, default=300, help="HTTP timeout in seconds; default 300")
    parser.add_argument("--output", type=Path, help="Optional JSON report output path")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    audio_path = args.audio.expanduser().resolve()
    dataset_root = args.dataset_root.expanduser().resolve()

    if not audio_path.is_file():
        print(f"ERROR: Audio file not found: {audio_path}", file=sys.stderr)
        return 2
    if not dataset_root.is_dir():
        print(f"ERROR: Dataset directory not found: {dataset_root}", file=sys.stderr)
        return 2

    try:
        reference, source_files = find_reference(dataset_root, audio_path.name)
        if reference is None:
            raise RuntimeError(
                f"No reference for {audio_path.name} found in any TSV beneath {dataset_root}. "
                "You can still test the endpoint, but automatic accuracy scoring requires the matching row."
            )
        result = transcribe(audio_path, args.api_base_url, args.endpoint_path, args.timeout)
    except (ValueError, RuntimeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    prediction = result["text"]
    metrics = calculate_metrics(reference, prediction)
    report = {
        "audio_file": str(audio_path),
        "reference_source_files": [str(p) for p in source_files],
        "endpoint": result["url"],
        "reference": reference,
        "prediction": prediction,
        "metrics": metrics,
        "status": result["payload"].get("status", "unknown"),
        "model_id": result["payload"].get("model_id", "unknown"),
    }

    print("--- SANTALI SINGLE-CLIP EVALUATION ---")
    print(f"Audio: {audio_path.name}")
    print(f"Reference TSV: {', '.join(str(p) for p in source_files)}")
    print(f"Endpoint: {result['url']}")
    print(f"Model: {report['model_id']}")
    print(f"Status: {report['status']}")
    print("\nREFERENCE:")
    print(reference)
    print("\nPREDICTION:")
    print(prediction)
    print("\nMETRICS:")
    print(f"Exact match: {metrics['exact_match']}")
    print(f"Spacing-only match: {metrics['spacing_only_match']}")
    print(f"CER (with spaces): {metrics['cer_with_spaces']:.4f} ({metrics['char_edits_with_spaces']} edits)")
    print(f"CER (without spaces): {metrics['cer_without_spaces']:.4f} ({metrics['char_edits_without_spaces']} edits)")
    print(f"WER: {metrics['wer']:.4f} ({metrics['word_edits']}/{metrics['reference_word_count']} word edits/words)")

    if args.output:
        output_path = args.output.expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nJSON report: {output_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
