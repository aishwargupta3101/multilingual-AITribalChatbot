"""Download AdiBhasha's Gondi training CSV after the user accepts its access terms."""
from __future__ import annotations

import os
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ID = "misniitdelhi/AdiBhasha"
REMOTE_FILE = "gondi/gondi-train.csv"
DEST = ROOT / "data" / "gondi" / "gondi-train.csv"


def main() -> int:
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass
    try:
        from huggingface_hub import hf_hub_download
    except ImportError:
        print("Missing huggingface_hub. Use the existing .venv: python -m pip install huggingface_hub")
        return 2
    token = os.getenv("HF_TOKEN", "").strip() or True  # use saved Hugging Face login if present
    try:
        cached_path = Path(
            hf_hub_download(
                repo_id=REPO_ID,
                filename=REMOTE_FILE,
                repo_type="dataset",
                token=token,
            )
        )
    except Exception as exc:
        print(f"Could not download AdiBhasha Gondi data: {type(exc).__name__}: {exc}")
        print("First sign in at https://huggingface.co/datasets/misniitdelhi/AdiBhasha and accept its access conditions.")
        print("Then run `hf auth login` in the same environment, or set HF_TOKEN in your existing .env.")
        print("Never paste your access token into this chat. The dataset is CC BY-NC-SA 4.0 (non-commercial).")
        return 2
    DEST.parent.mkdir(parents=True, exist_ok=True)
    if cached_path.resolve() != DEST.resolve():
        shutil.copy2(cached_path, DEST)
    print("SUCCESS: downloaded the Gondi training CSV")
    print(f"File: {DEST}")
    print("The dataset license is CC BY-NC-SA 4.0; do not use it commercially without separate permission.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
