"""Local Hindi <-> Gondi MT5 translation service.

The model is deliberately loaded from a local fine-tuned checkpoint only. This
module never silently falls back to English or a different tribal language.
"""
from __future__ import annotations

import logging
import os
import threading
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


def _project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _model_dir() -> Path:
    configured = os.getenv("GONDI_MT5_MODEL_DIR", "models/gondi_mt5").strip()
    candidate = Path(configured).expanduser()
    return candidate.resolve() if candidate.is_absolute() else (_project_root() / candidate).resolve()


class GondiLocalTranslationService:
    """Hindi/Gondi translator backed by the project's fine-tuned mT5 checkpoint."""

    def __init__(self) -> None:
        self._model: Any = None
        self._tokenizer: Any = None
        self._device: str | None = None
        self._lock = threading.Lock()

    @staticmethod
    def checkpoint_available() -> bool:
        folder = _model_dir()
        return folder.is_dir() and (folder / "config.json").is_file() and any(
            (folder / name).is_file()
            for name in ("model.safetensors", "pytorch_model.bin", "model.safetensors.index.json")
        )

    def status(self) -> dict[str, Any]:
        ready = self.checkpoint_available()
        return {
            "language": "gondi",
            "translation_provider": "local fine-tuned google/mt5-small",
            "translation_model_dir": str(_model_dir()),
            "translation_ready": ready,
            "translation_state": "ready" if ready else "training_required",
            "supported_translation_pairs": ["Hindi <-> Gondi (Devanagari training script)"],
            "note": "No translation output is fabricated if the trained model is missing.",
        }

    def _load(self) -> None:
        if self._model is not None and self._tokenizer is not None:
            return
        with self._lock:
            if self._model is not None and self._tokenizer is not None:
                return
            folder = _model_dir()
            if not self.checkpoint_available():
                raise RuntimeError(
                    "The local Gondi translation model has not been trained yet. "
                    "First download the approved AdiBhasha Gondi CSV, then run "
                    "python scripts/train_gondi_mt5.py. The trained checkpoint is expected at "
                    f"{folder}."
                )
            try:
                import torch
                from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            except ImportError as exc:
                raise RuntimeError(
                    "Gondi translation requires the existing environment's torch and transformers packages."
                ) from exc
            try:
                tokenizer = AutoTokenizer.from_pretrained(str(folder), local_files_only=True)
                model = AutoModelForSeq2SeqLM.from_pretrained(str(folder), local_files_only=True)
                device = "cuda" if torch.cuda.is_available() else "cpu"
                model.to(device)
                model.eval()
            except Exception as exc:
                logger.exception("Could not load local Gondi MT5 checkpoint.")
                raise RuntimeError(
                    f"Could not load the trained Gondi translation checkpoint ({type(exc).__name__}). "
                    "Check the model files in models/gondi_mt5."
                ) from exc
            self._tokenizer, self._model, self._device = tokenizer, model, device
            logger.info("Loaded local Gondi mT5 checkpoint on %s from %s", device, folder)

    def translate(self, text: str, direction: str) -> str:
        value = str(text or "").strip()
        if not value:
            raise ValueError("Gondi translation input is empty.")
        if len(value) > 3000:
            raise ValueError("Gondi translation accepts at most 3000 characters per request.")
        direction = str(direction or "").strip().lower().replace("-", "_")
        prefixes = {
            "hindi_to_gondi": "translate Hindi to Gondi:",
            "gondi_to_hindi": "translate Gondi to Hindi:",
        }
        if direction not in prefixes:
            raise ValueError("The local Gondi model supports Hindi-to-Gondi and Gondi-to-Hindi only.")
        self._load()
        import torch

        inputs = self._tokenizer(
            f"{prefixes[direction]} {value}",
            return_tensors="pt",
            truncation=True,
            max_length=256,
        )
        inputs = {key: tensor.to(self._device) for key, tensor in inputs.items()}
        try:
            with torch.inference_mode():
                output_ids = self._model.generate(
                    **inputs,
                    max_new_tokens=192,
                    num_beams=2,
                    early_stopping=True,
                )
            translated = self._tokenizer.decode(output_ids[0], skip_special_tokens=True).strip()
        except Exception as exc:
            logger.exception("Local Gondi mT5 translation inference failed.")
            raise RuntimeError(f"Gondi translation inference failed ({type(exc).__name__}).") from exc
        if not translated:
            raise RuntimeError("The trained Gondi model returned an empty translation.")
        return translated


gondi_local_translation_service = GondiLocalTranslationService()
