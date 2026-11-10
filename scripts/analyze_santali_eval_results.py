"""Analyze an existing Santali Common Voice evaluation CSV without loading a model.

Usage from the project root:
  python scripts/analyze_santali_eval_results.py "C:\\Users\\kunda\\Downloads\\santali_onnx_eval_50.csv"

Outputs by default beside the input:
  santali_onnx_eval_50_diagnostics.csv
  santali_onnx_eval_50_summary.txt

This script is read-only with respect to the original CSV and does not touch the
API, model files, environment variables, or any existing chatbot modules.
"""
from __future__ import annotations

import argparse
import csv
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Sequence

REQUIRED_COLUMNS = {"sample_index", "audio_filename", "reference", "prediction"}
CLASS_LABELS = {
    "exact_match": "Exact text match",
    "spacing_only": "Whitespace/word-boundary difference only",
    "character_level_difference": "Character-level difference (not spacing alone)",
}


def normalize(text: str, *, keep_spaces: bool = True) -> str:
    text = unicodedata.normalize("NFC", str(text or ""))
    text = " ".join(text.split())
    return text if keep_spaces else "".join(text.split())


def edit_distance(reference: Sequence[str] | str, hypothesis: Sequence[str] | str) -> int:
    """Levenshtein distance for strings or token sequences, using O(min(n,m)) memory."""
    if len(hypothesis) > len(reference):
        reference, hypothesis = hypothesis, reference
    previous = list(range(len(hypothesis) + 1))
    for i, ref_item in enumerate(reference, start=1):
        current = [i]
        for j, hyp_item in enumerate(hypothesis, start=1):
            current.append(min(
                current[-1] + 1,
                previous[j] + 1,
                previous[j - 1] + (ref_item != hyp_item),
            ))
        previous = current
    return previous[-1]


def classify(reference: str, prediction: str) -> str:
    ref_norm = normalize(reference)
    hyp_norm = normalize(prediction)
    if ref_norm == hyp_norm:
        return "exact_match"
    if normalize(ref_norm, keep_spaces=False) == normalize(hyp_norm, keep_spaces=False):
        return "spacing_only"
    return "character_level_difference"


def analyze_record(row: dict[str, str]) -> dict[str, str]:
    reference = row.get("reference", "") or ""
    prediction = row.get("prediction", "") or ""
    ref_norm = normalize(reference)
    hyp_norm = normalize(prediction)
    ref_no_spaces = normalize(reference, keep_spaces=False)
    hyp_no_spaces = normalize(prediction, keep_spaces=False)

    char_edits_spaces = edit_distance(ref_norm, hyp_norm)
    char_edits_no_spaces = edit_distance(ref_no_spaces, hyp_no_spaces)
    ref_words = ref_norm.split()
    hyp_words = hyp_norm.split()
    word_edits = edit_distance(ref_words, hyp_words)

    out = dict(row)
    out.update({
        "evaluation_class": classify(reference, prediction),
        "reference_normalized": ref_norm,
        "prediction_normalized": hyp_norm,
        "reference_chars_with_spaces": str(len(ref_norm)),
        "char_edits_with_spaces": str(char_edits_spaces),
        "cer_recomputed_with_spaces": f"{char_edits_spaces / len(ref_norm) if ref_norm else 0.0:.4f}",
        "reference_chars_without_spaces": str(len(ref_no_spaces)),
        "char_edits_without_spaces": str(char_edits_no_spaces),
        "cer_recomputed_without_spaces": f"{char_edits_no_spaces / len(ref_no_spaces) if ref_no_spaces else 0.0:.4f}",
        "reference_word_count": str(len(ref_words)),
        "word_edits_recomputed": str(word_edits),
        "wer_recomputed": f"{word_edits / len(ref_words) if ref_words else 0.0:.4f}",
    })
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify Santali evaluation errors without rerunning inference.")
    parser.add_argument("input_csv", help="Existing CSV from evaluate_santali_common_voice.py")
    parser.add_argument("--output-csv", default="", help="Diagnostics CSV path (default: <input stem>_diagnostics.csv)")
    parser.add_argument("--summary", default="", help="Summary text path (default: <input stem>_summary.txt)")
    parser.add_argument("--worst-count", type=int, default=10, help="Number of highest-WER examples listed in summary (default 10)")
    args = parser.parse_args()
    if args.worst_count < 0:
        parser.error("--worst-count must be zero or greater")

    input_path = Path(args.input_csv).expanduser().resolve()
    if not input_path.is_file():
        print(f"ERROR: Input CSV does not exist: {input_path}", file=sys.stderr)
        return 2

    output_csv = Path(args.output_csv).expanduser().resolve() if args.output_csv else input_path.with_name(f"{input_path.stem}_diagnostics.csv")
    summary_path = Path(args.summary).expanduser().resolve() if args.summary else input_path.with_name(f"{input_path.stem}_summary.txt")

    try:
        with input_path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            if reader.fieldnames is None:
                raise ValueError("CSV has no header row")
            missing = REQUIRED_COLUMNS - set(reader.fieldnames)
            if missing:
                raise ValueError("Missing required columns: " + ", ".join(sorted(missing)))
            source_rows = list(reader)
    except (OSError, UnicodeError, csv.Error, ValueError) as exc:
        print(f"ERROR: Could not read input CSV: {exc}", file=sys.stderr)
        return 2

    if not source_rows:
        print("ERROR: Input CSV contains no evaluation rows.", file=sys.stderr)
        return 2

    records = [analyze_record(row) for row in source_rows]
    counts = Counter(r["evaluation_class"] for r in records)
    sum_cer_space_edits = sum(int(r["char_edits_with_spaces"]) for r in records)
    sum_cer_space_chars = sum(int(r["reference_chars_with_spaces"]) for r in records)
    sum_cer_no_space_edits = sum(int(r["char_edits_without_spaces"]) for r in records)
    sum_cer_no_space_chars = sum(int(r["reference_chars_without_spaces"]) for r in records)
    sum_word_edits = sum(int(r["word_edits_recomputed"]) for r in records)
    sum_ref_words = sum(int(r["reference_word_count"]) for r in records)

    output_csv.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(records[0].keys())
    try:
        with output_csv.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(records)
    except OSError as exc:
        print(f"ERROR: Could not write diagnostics CSV: {exc}", file=sys.stderr)
        return 2

    exact = counts["exact_match"]
    spacing = counts["spacing_only"]
    char_level = counts["character_level_difference"]
    cer_spaces = sum_cer_space_edits / sum_cer_space_chars if sum_cer_space_chars else 0.0
    cer_no_spaces = sum_cer_no_space_edits / sum_cer_no_space_chars if sum_cer_no_space_chars else 0.0
    wer = sum_word_edits / sum_ref_words if sum_ref_words else 0.0

    summary_lines = [
        "SANTALI ONNX EVALUATION DIAGNOSTICS",
        "====================================",
        f"Input CSV: {input_path}",
        f"Samples: {len(records)}",
        "",
        "Classification (mutually exclusive):",
        f"  Exact text matches: {exact}/{len(records)} ({exact / len(records):.1%})",
        f"  Whitespace/word-boundary only: {spacing}/{len(records)} ({spacing / len(records):.1%})",
        f"  Character-level differences: {char_level}/{len(records)} ({char_level / len(records):.1%})",
        "",
        "Recomputed aggregate metrics:",
        f"  CER with spaces: {cer_spaces:.4f} ({cer_spaces:.2%})",
        f"  CER without spaces: {cer_no_spaces:.4f} ({cer_no_spaces:.2%})",
        f"  WER: {wer:.4f} ({wer:.2%})",
        f"  Word edit count / reference words: {sum_word_edits} / {sum_ref_words}",
        "",
        "Interpretation:",
        "  Spacing-only rows have matching character sequences after all whitespace is removed.",
        "  Character-level-difference rows include at least one non-whitespace character difference.",
        "  These automatic labels do not judge whether the reference transcript itself is correct.",
        "  The sample is a technical evaluation, not native-speaker certification or production validation.",
        "",
        "Highest-WER samples (recomputed):",
    ]
    if args.worst_count:
        worst = sorted(records, key=lambda r: (float(r["wer_recomputed"]), int(r["word_edits_recomputed"])), reverse=True)[:args.worst_count]
        for row in worst:
            summary_lines.append(
                f"  #{row.get('sample_index', '?')} {row.get('audio_filename', '?')}: "
                f"class={row['evaluation_class']}, WER={row['wer_recomputed']}, "
                f"CER-no-spaces={row['cer_recomputed_without_spaces']}"
            )
    else:
        summary_lines.append("  (omitted by --worst-count 0)")
    summary_lines += [
        "",
        "Safety note: This tool does not load or execute the model, change API flags, or alter the source CSV.",
        "Keep TRIBAL_SANTALI_ONNX_STT_ENABLED=false until broader evaluation and language review are complete.",
    ]
    try:
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: Could not write summary: {exc}", file=sys.stderr)
        return 2

    print("--- SANTALI EVALUATION DIAGNOSTICS ---")
    print(f"Samples: {len(records)}")
    print(f"Exact text matches: {exact}")
    print(f"Whitespace/word-boundary only: {spacing}")
    print(f"Character-level differences: {char_level}")
    print(f"Aggregate CER with spaces: {cer_spaces:.4f}")
    print(f"Aggregate CER without spaces: {cer_no_spaces:.4f}")
    print(f"Aggregate WER: {wer:.4f} ({sum_word_edits}/{sum_ref_words} word edits/words)")
    print(f"Diagnostics CSV: {output_csv}")
    print(f"Summary: {summary_path}")
    print("No model inference was performed; no API or environment settings were changed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
