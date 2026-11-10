"""Run a safe Santali preflight. Does not download model weights or enable routes.

From the project root:
    python scripts/check_santali_readiness.py

If HF_TOKEN is set and repository conditions have been accepted in your own HF
account, the script downloads only each model repository's small README.md to a
temporary folder and removes it. It never prints the token.
"""
from __future__ import annotations

import json
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

from backend.tribal_languages.santali_readiness import (
    configuration_report,
    dependency_report,
    probe_required_repositories,
    resource_report,
)


def main() -> int:
    token = os.getenv("HF_TOKEN", "").strip()
    report = {
        "check": "santali-model-readiness-preflight",
        "downloads_model_weights": False,
        "enables_inference": False,
        "dependencies": dependency_report(),
        "configuration": configuration_report(),
        "resources": resource_report(),
        "repository_access": (
            probe_required_repositories(token) if token else [
                {"status": "skipped_no_HF_TOKEN", "readme_accessible": False,
                 "note": "Set HF_TOKEN only after you personally accept the relevant Hugging Face repository conditions."}
            ]
        ),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
