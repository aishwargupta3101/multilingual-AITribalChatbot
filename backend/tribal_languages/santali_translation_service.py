"""Bidirectional Santali (Ol Chiki) <-> English translation using IndicTrans2.

Models load lazily, and only one direction's weights are kept in this process at a
 time to reduce peak RAM. Translation quality remains unvalidated for production.
"""
from __future__ import annotations

import gc
import os
import threading
from typing import Any

LANG_SANTALI = "sat_Olck"
LANG_ENGLISH = "eng_Latn"
MODEL_SAT_TO_EN = os.getenv(
    "TRIBAL_SANTALI_TO_EN_MODEL", "ai4bharat/indictrans2-indic-en-dist-200M"
)
MODEL_EN_TO_SAT = os.getenv(
    "TRIBAL_EN_TO_SANTALI_MODEL", "ai4bharat/indictrans2-en-indic-dist-200M"
)
MAX_TRANSLATION_CHARS = 3000
MIN_AVAILABLE_RAM_GB = float(os.getenv("TRIBAL_SANTALI_TRANSLATION_MIN_RAM_GB", "1.4"))

_LOCK = threading.RLock()
_ACTIVE_DIRECTION: str | None = None
_ACTIVE_RESOURCES: tuple[Any, Any, Any, Any, str] | None = None


def _load_environment() -> None:
    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)
    except ImportError:
        pass


def _check_memory() -> None:
    try:
        import psutil
    except ImportError:
        return
    available_gb = psutil.virtual_memory().available / (1024 ** 3)
    if available_gb < MIN_AVAILABLE_RAM_GB:
        raise RuntimeError(
            f"Only {available_gb:.2f} GB RAM is available. Santali translation needs "
            f"at least {MIN_AVAILABLE_RAM_GB:.1f} GB available RAM to start safely. "
            "Close memory-heavy apps/models and retry."
        )


def _model_config(direction: str) -> tuple[str, str, str]:
    if direction == "sat_to_en":
        return MODEL_SAT_TO_EN, LANG_SANTALI, LANG_ENGLISH
    if direction == "en_to_sat":
        return MODEL_EN_TO_SAT, LANG_ENGLISH, LANG_SANTALI
    raise ValueError(f"Unsupported Santali translation direction: {direction}")


def _load_resources(direction: str) -> tuple[Any, Any, Any, Any, str]:
    global _ACTIVE_DIRECTION, _ACTIVE_RESOURCES
    with _LOCK:
        if _ACTIVE_DIRECTION == direction and _ACTIVE_RESOURCES is not None:
            return _ACTIVE_RESOURCES

        _check_memory()
        _load_environment()
        try:
            import torch
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            try:
                # Current IndicTransToolkit examples export IndicProcessor at package root.
                from IndicTransToolkit import IndicProcessor
            except ImportError:
                # Retain compatibility with builds exposing the processor submodule.
                from IndicTransToolkit.processor import IndicProcessor
        except ImportError as exc:
            raise RuntimeError(
                "Santali translation dependencies are missing. Install the required "
                "packages already listed in the project's existing requirements.txt."
            ) from exc

        # Release the opposite direction's model before loading the next one.
        _ACTIVE_RESOURCES = None
        _ACTIVE_DIRECTION = None
        gc.collect()
        if torch.cuda.is_available():
            try:
                torch.cuda.empty_cache()
            except Exception:
                pass

        model_id, _, _ = _model_config(direction)
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
        kwargs: dict[str, Any] = {"trust_remote_code": True}
        if token:
            kwargs["token"] = token
        try:
            tokenizer = AutoTokenizer.from_pretrained(model_id, **kwargs)
            model = AutoModelForSeq2SeqLM.from_pretrained(model_id, **kwargs)
        except Exception as exc:
            message = str(exc).lower()
            if any(x in message for x in ("gated repo", "gated repository", "401", "403", "access to this model")):
                raise RuntimeError(
                    f"Access to {model_id} was denied. Sign in to Hugging Face, accept that model's "
                    "conditions, and ensure HF_TOKEN is available to the running process. "
                    "Never paste your token into chat."
                ) from exc
            raise RuntimeError(
                f"Could not load translation model {model_id}: {type(exc).__name__}: {exc}"
            ) from exc

        device = "cuda" if torch.cuda.is_available() else "cpu"
        model.to(device)
        model.eval()
        processor = IndicProcessor(inference=True)
        _ACTIVE_RESOURCES = (tokenizer, model, processor, torch, device)
        _ACTIVE_DIRECTION = direction
        return _ACTIVE_RESOURCES


def _translate(text: str, direction: str) -> str:
    clean = str(text or "").strip()
    if not clean:
        raise ValueError("Translation input is empty.")
    if len(clean) > MAX_TRANSLATION_CHARS:
        raise ValueError(
            f"Text is too long ({len(clean)} characters). Limit: {MAX_TRANSLATION_CHARS}."
        )

    model_id, src_lang, tgt_lang = _model_config(direction)
    tokenizer, model, processor, torch, device = _load_resources(direction)
    try:
        prepared = processor.preprocess_batch([clean], src_lang=src_lang, tgt_lang=tgt_lang)
        encoded = tokenizer(
            prepared,
            truncation=True,
            padding="longest",
            return_tensors="pt",
            return_attention_mask=True,
        )
        encoded = {key: value.to(device) for key, value in encoded.items()}
        with torch.inference_mode():
            generated = model.generate(
                **encoded,
                use_cache=True,
                num_beams=4,
                max_new_tokens=256,
                num_return_sequences=1,
            )
        decoded = tokenizer.batch_decode(
            generated, skip_special_tokens=True, clean_up_tokenization_spaces=True
        )
        postprocessed = processor.postprocess_batch(decoded, lang=tgt_lang)
        result = str(postprocessed[0] if postprocessed else "").strip()
        if not result:
            raise RuntimeError(f"Translation model {model_id} returned empty text.")
        return result
    except (ValueError, RuntimeError):
        raise
    except Exception as exc:
        raise RuntimeError(
            f"Translation failed with {model_id}: {type(exc).__name__}: {exc}"
        ) from exc


def translate_santali_to_english(text: str) -> str:
    return _translate(text, "sat_to_en")


def translate_english_to_santali(text: str) -> str:
    return _translate(text, "en_to_sat")


def translation_status() -> dict[str, str]:
    return {
        "santali_to_english_model": MODEL_SAT_TO_EN,
        "english_to_santali_model": MODEL_EN_TO_SAT,
        "loading_strategy": "one-directional-model-in-memory-at-a-time",
        "active_direction": _ACTIVE_DIRECTION or "not_loaded",
    }
