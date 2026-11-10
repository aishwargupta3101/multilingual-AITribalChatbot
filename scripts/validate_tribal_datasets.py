
"""Usage: python scripts/validate_tribal_datasets.py data/tribal_languages/dataset_manifest.json"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

# Allows execution from repository root without installing the project.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.tribal_languages.dataset_validator import validate_manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate local tribal-language dataset manifest and audio files.")
    parser.add_argument("manifest", help="Path to dataset manifest JSON")
    parser.add_argument("--dataset-root", help="Root for relative audio_path values (default: manifest's directory)")
    args = parser.parse_args()
    report = validate_manifest(args.manifest, args.dataset_root)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
