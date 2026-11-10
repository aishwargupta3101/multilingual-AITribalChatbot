
"""Run the experimental tribal-language unit-test suites without starting the API."""
from __future__ import annotations
import subprocess
import sys

MODULES = [
    "tests.test_tribal_stt_service",
    "tests.test_tribal_translation_service",
    "tests.test_tribal_tts_service",
    "tests.test_tribal_language_router",
    "tests.test_tribal_dataset_validator",
    "tests.test_tribal_model_evaluation",
]


def main() -> int:
    failed = []
    for module in MODULES:
        print(f"\n{'=' * 72}\nRunning {module}\n{'=' * 72}", flush=True)
        result = subprocess.run([sys.executable, "-m", "unittest", module, "-v"])
        if result.returncode:
            failed.append(module)
    print("\n" + "=" * 72)
    if failed:
        print("FAILED TEST MODULES:")
        for module in failed:
            print(f" - {module}")
        print("Fix or investigate failures before integration/deployment.")
        return 1
    print("All listed tribal-language unit-test modules passed.")
    print("Note: passing unit tests do not prove model accuracy or language coverage.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
