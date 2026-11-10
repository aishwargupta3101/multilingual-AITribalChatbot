
"""Usage: python scripts/validate_model_evaluations.py data/tribal_languages/model_evaluation.json"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from backend.tribal_languages.model_evaluation import validate_evaluation_records


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate recorded tribal-language model evaluation evidence.")
    parser.add_argument("evaluation_file")
    args = parser.parse_args()
    report = validate_evaluation_records(args.evaluation_file)
    print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
