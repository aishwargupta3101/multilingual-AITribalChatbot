"""Run live English -> target -> English checks for central translation routes.

Run from the project root:
    python scripts/test_translation_matrix.py

This is an inference smoke test, not a linguistic-quality benchmark. It may
load/download large models and can take several minutes on CPU.
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
from backend.services.translation_service import translation_service

SOURCE_TEXT = "Artificial intelligence is useful."


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", nargs="*", help="Optional language names to test")
    parser.add_argument("--json", dest="json_path", help="Also write results to a JSON file")
    args = parser.parse_args()

    languages = sorted(translation_service.SUPPORTED_LANGUAGES - {"english"})
    if args.only:
        requested = {translation_service.normalize_language(item) for item in args.only}
        unknown = requested - translation_service.SUPPORTED_LANGUAGES
        if unknown:
            parser.error("Unsupported language(s): " + ", ".join(sorted(unknown)))
        languages = sorted(requested - {"english"})

    results = []
    print("\n=== TRANSLATION MATRIX: English -> target -> English ===\n")
    for language in languages:
        item = {"language": language, "forward": "not_run", "reverse": "not_run", "ok": False}
        started = time.perf_counter()
        try:
            translated = translation_service.translate_response(
                text=SOURCE_TEXT,
                source_language="english",
                target_language=language,
            )
            item["forward"] = translated
            if not translated or not translated.strip():
                raise ValueError("Forward translation was empty")
            if translated.strip() == SOURCE_TEXT:
                raise ValueError("Forward translation was unchanged English text")

            back_translated = translation_service.translate_response(
                text=translated,
                source_language=language,
                target_language="english",
            )
            item["reverse"] = back_translated
            if not back_translated or not back_translated.strip():
                raise ValueError("Reverse translation was empty")
            item["ok"] = True
            print(f"[PASS] {language}")
            print(f"       target: {translated}")
            print(f"       back:   {back_translated}")
        except Exception as exc:
            item["error"] = f"{type(exc).__name__}: {exc}"
            print(f"[FAIL] {language}: {item['error']}")
        item["seconds"] = round(time.perf_counter() - started, 2)
        results.append(item)

    passed = sum(bool(item["ok"]) for item in results)
    failed = len(results) - passed
    print(f"\nSUMMARY: {passed} passed, {failed} failed, {len(results)} tested")
    if args.json_path:
        output = Path(args.json_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(json.dumps({"source_text": SOURCE_TEXT, "results": results}, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Saved report: {output}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
