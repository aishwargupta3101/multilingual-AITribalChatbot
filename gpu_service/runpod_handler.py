"""
RunPod Serverless handler for the Tribal IndicTrans2 GPU service.

The IndicTrans2 runtime below is adapted from the supplied Modal implementation.
Language codes, aliases, model IDs, preprocessing, batching, and generation
settings are intentionally preserved.
"""

import gc
import logging
import os
import shutil
import threading
from pathlib import Path
from functools import lru_cache

import runpod

logging.basicConfig(level=os.environ.get("LOG_LEVEL", "INFO"))
logger = logging.getLogger("tribal-indictrans-runpod")


class IndicTransRuntime:

    LANGUAGE_CODES = {
        "english": "eng_Latn",
        "hindi": "hin_Deva",
        "manipuri": "mni_Beng",
        "manipuri_beng": "mni_Beng",
        "manipuri_bengali": "mni_Beng",
        "manipuri_mtei": "mni_Mtei",
        "manipuri_mayek": "mni_Mtei",
        "assamese": "asm_Beng",
        "bengali": "ben_Beng",
        "bodo": "brx_Deva",
        "dogri": "doi_Deva",
        "gujarati": "guj_Gujr",
        "kannada": "kan_Knda",
        "kashmiri": "kas_Arab",
        "kashmiri_deva": "kas_Deva",
        "konkani": "gom_Deva",
        "maithili": "mai_Deva",
        "malayalam": "mal_Mlym",
        "marathi": "mar_Deva",
        "nepali": "npi_Deva",
        "odia": "ory_Orya",
        "punjabi": "pan_Guru",
        "sanskrit": "san_Deva",
        "santali": "sat_Olck",
        "sindhi": "snd_Arab",
        "sindhi_deva": "snd_Deva",
        "tamil": "tam_Taml",
        "telugu": "tel_Telu",
        "urdu": "urd_Arab",
    }

    LANGUAGE_ALIASES = {
        "en": "english",
        "eng": "english",
        "hi": "hindi",
        "hin": "hindi",
        "meitei": "manipuri_mtei",
        "meitei_mayek": "manipuri_mtei",
        "manipuri_meitei": "manipuri_mtei",
        "mni_beng": "manipuri",
        "mni_mtei": "manipuri_mtei",
        "as": "assamese",
        "asm": "assamese",
        "bn": "bengali",
        "ben": "bengali",
        "brx": "bodo",
        "doi": "dogri",
        "gu": "gujarati",
        "guj": "gujarati",
        "kn": "kannada",
        "kan": "kannada",
        "ks": "kashmiri",
        "kas": "kashmiri",
        "kas_deva": "kashmiri_deva",
        "gom": "konkani",
        "mai": "maithili",
        "ml": "malayalam",
        "mal": "malayalam",
        "mr": "marathi",
        "mar": "marathi",
        "ne": "nepali",
        "npi": "nepali",
        "or": "odia",
        "ory": "odia",
        "pa": "punjabi",
        "pan": "punjabi",
        "sa": "sanskrit",
        "san": "sanskrit",
        "sd": "sindhi",
        "snd": "sindhi",
        "snd_deva": "sindhi_deva",
        "ta": "tamil",
        "tam": "tamil",
        "te": "telugu",
        "tel": "telugu",
        "ur": "urdu",
        "sat": "santali",
        "sat_olck": "santali",
    }

    MODEL_EN_INDIC = "ai4bharat/indictrans2-en-indic-1B"
    MODEL_INDIC_EN = "ai4bharat/indictrans2-indic-en-1B"
    MODEL_INDIC_INDIC = "ai4bharat/indictrans2-indic-indic-1B"

    MAX_INPUT_LENGTH = 256
    MAX_NEW_TOKENS = 128
    MAX_BATCH_SIZE = 8

    def __init__(self):
        import torch

        if not torch.cuda.is_available():
            raise RuntimeError(
                "CUDA GPU is not available inside the Modal container."
            )

        self.torch = torch
        self.device = torch.device("cuda")

        self.model = None
        self.tokenizer = None
        self.processor = None
        self.active_model_name = None

        self.lock = threading.RLock()
        self.cache_dir = Path(os.environ.get("HF_HOME", "/runpod-volume/huggingface")) / "indictrans2"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logger.info("IndicTrans2 cache directory: %s", self.cache_dir)
        logger.info("Network volume mount exists: %s", Path("/runpod-volume").exists())
        logger.info(
            "IndicTrans2 runtime initialized on %s",
            torch.cuda.get_device_name(0),
        )

    @classmethod
    def normalize_language(cls, language):
        if not language:
            raise ValueError("Language cannot be empty.")

        language = (
            str(language)
            .lower()
            .strip()
            .replace("-", "_")
            .replace(" ", "_")
        )

        return cls.LANGUAGE_ALIASES.get(language, language)

    @classmethod
    def validate_language(cls, language):
        if language not in cls.LANGUAGE_CODES:
            raise ValueError(
                f"IndicTrans2 does not support language: {language}"
            )

    def get_model_name(self, source_language, target_language):
        if source_language == "english":
            return self.MODEL_EN_INDIC

        if target_language == "english":
            return self.MODEL_INDIC_EN

        return self.MODEL_INDIC_INDIC

    def release_model(self):
        self.model = None
        self.tokenizer = None
        self.processor = None
        self.active_model_name = None

        gc.collect()
        self.torch.cuda.empty_cache()

    def load_model(self, model_name):
        if (
            self.active_model_name == model_name
            and self.model is not None
        ):
            return

        self.release_model()

        from transformers import (
            AutoModelForSeq2SeqLM,
            AutoTokenizer,
        )
        from IndicTransToolkit import IndicProcessor

        logging.info("Loading IndicTrans2 model: %s", model_name)
        logging.info("IndicTrans2 stage: loading tokenizer")

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir=str(self.cache_dir),
        )

        logging.info("IndicTrans2 stage: loading seq2seq model")
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir=str(self.cache_dir),
            low_cpu_mem_usage=True,
        )

        logging.info("IndicTrans2 stage: moving model to CUDA and converting to FP16")
        self.model.to(self.device)
        self.model.half()
        self.model.eval()

        self.processor = IndicProcessor(inference=True)
        self.active_model_name = model_name

        logging.info("Model loaded successfully: %s", model_name)

    def translate_batch(
        self,
        texts,
        source_language,
        target_language,
        batch_size=8,
    ):
        source_language = self.normalize_language(source_language)
        target_language = self.normalize_language(target_language)

        self.validate_language(source_language)
        self.validate_language(target_language)

        cleaned = [str(item or "").strip() for item in texts]
        results = [""] * len(cleaned)

        indexed = [
            (index, item)
            for index, item in enumerate(cleaned)
            if item
        ]

        if not indexed:
            return results

        if source_language == target_language:
            for index, item in indexed:
                results[index] = item
            return results

        model_name = self.get_model_name(
            source_language,
            target_language,
        )

        source_code = self.LANGUAGE_CODES[source_language]
        target_code = self.LANGUAGE_CODES[target_language]

        batch_size = max(
            1,
            min(int(batch_size), self.MAX_BATCH_SIZE),
        )

        with self.lock:
            self.load_model(model_name)

            for offset in range(0, len(indexed), batch_size):
                batch = indexed[offset:offset + batch_size]

                batch_texts = [item for _, item in batch]

                logging.info("IndicTrans2 stage: preprocessing batch (items=%d, src=%s, tgt=%s)", len(batch_texts), source_code, target_code)
                processed_texts = self.processor.preprocess_batch(
                    batch_texts,
                    src_lang=source_code,
                    tgt_lang=target_code,
                )

                logging.info("IndicTrans2 stage: tokenizing batch")
                inputs = self.tokenizer(
                    processed_texts,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=self.MAX_INPUT_LENGTH,
                )

                inputs = {
                    key: value.to(self.device)
                    for key, value in inputs.items()
                }

                generation_args = {
                    "max_new_tokens": self.MAX_NEW_TOKENS,
                    "num_beams": 1,
                    "do_sample": False,
                    "use_cache": True,
                }

                logging.info("IndicTrans2 stage: generating translation tokens")
                with self.torch.inference_mode():
                    generated_tokens = self.model.generate(
                        **inputs,
                        **generation_args,
                    )

                logging.info("IndicTrans2 stage: decoding generated tokens")
                decoded = self.tokenizer.batch_decode(
                    generated_tokens,
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=True,
                )

                logging.info("IndicTrans2 stage: postprocessing translation")
                postprocessed = self.processor.postprocess_batch(
                    decoded,
                    lang=target_code,
                )

                if len(postprocessed) != len(batch):
                    raise ValueError(
                        "IndicTrans2 returned an unexpected batch size."
                    )

                for (original_index, _), output in zip(
                    batch,
                    postprocessed,
                ):
                    output = (output or "").strip()

                    if not output:
                        raise ValueError(
                            "IndicTrans2 returned an empty translation."
                        )

                    results[original_index] = output

        return results

    @lru_cache(maxsize=512)
    def translate_cached(
        self,
        text,
        source_language,
        target_language,
    ):
        return self.translate_batch(
            [text],
            source_language,
            target_language,
            batch_size=1,
        )[0]

    def translate(self, text, source_language, target_language):
        if not text or not str(text).strip():
            return ""

        source_language = self.normalize_language(source_language)
        target_language = self.normalize_language(target_language)

        self.validate_language(source_language)
        self.validate_language(target_language)

        if source_language == target_language:
            return str(text).strip()

        return self.translate_cached(
            str(text).strip(),
            source_language,
            target_language,
        )

_RUNTIME = None
_RUNTIME_LOCK = threading.Lock()


def get_runtime():
    """Create one runtime per warm worker and reuse it for later jobs."""
    global _RUNTIME
    if _RUNTIME is None:
        with _RUNTIME_LOCK:
            if _RUNTIME is None:
                _RUNTIME = IndicTransRuntime()
    return _RUNTIME


def get_storage_status():
    """Inspect the mounted persistent volume without loading a GPU model."""
    mount_path = Path("/runpod-volume")
    hf_home = Path(os.environ.get("HF_HOME", "/runpod-volume/huggingface"))
    cache_dir = hf_home / "indictrans2"
    result = {
        "mount_path": str(mount_path),
        "mount_exists": mount_path.exists(),
        "mount_is_directory": mount_path.is_dir(),
        "hf_home": str(hf_home),
        "cache_dir": str(cache_dir),
        "cache_exists": cache_dir.exists(),
        "cache_entries": [],
        "writable": False,
        "disk_total_gb": None,
        "disk_used_gb": None,
        "disk_free_gb": None,
    }

    if mount_path.exists():
        try:
            usage = shutil.disk_usage(mount_path)
            result.update({
                "disk_total_gb": round(usage.total / (1024 ** 3), 2),
                "disk_used_gb": round(usage.used / (1024 ** 3), 2),
                "disk_free_gb": round(usage.free / (1024 ** 3), 2),
            })
            probe = mount_path / ".tribal_indictrans_write_test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink(missing_ok=True)
            result["writable"] = True
        except Exception as exc:
            result["write_error"] = f"{type(exc).__name__}: {exc}"

    if cache_dir.exists() and cache_dir.is_dir():
        try:
            result["cache_entries"] = sorted(item.name for item in cache_dir.iterdir())[:50]
        except Exception as exc:
            result["cache_list_error"] = f"{type(exc).__name__}: {exc}"

    result["hf_token_configured"] = bool(os.environ.get("HF_TOKEN") or os.environ.get("HUGGING_FACE_HUB_TOKEN"))
    return result


def handler(job):
    """RunPod Serverless job handler."""
    job_input = (job or {}).get("input") or {}
    if not isinstance(job_input, dict):
        return {"error": "Job input must be a JSON object."}

    action = str(job_input.get("action", "translate")).strip().lower()

    try:
        # Storage diagnostics intentionally avoid initializing CUDA or loading models.
        if action in {"storage", "storage_health"}:
            return {"status": "ok", "storage": get_storage_status()}

        runtime = get_runtime()

        if action == "health":
            return {
                "status": "healthy",
                "service": "Tribal IndicTrans2 GPU",
                "device": str(runtime.device),
                "gpu": runtime.torch.cuda.get_device_name(0),
                "active_model": runtime.active_model_name,
                "storage": get_storage_status(),
            }

        source_language = job_input.get("source_language")
        target_language = job_input.get("target_language")
        if not source_language or not target_language:
            return {
                "error": "source_language and target_language are required."
            }

        if isinstance(job_input.get("texts"), list):
            translations = runtime.translate_batch(
                job_input["texts"],
                source_language,
                target_language,
                job_input.get("batch_size", 8),
            )
            return {
                "translations": translations,
                "source_language": source_language,
                "target_language": target_language,
            }

        if "text" not in job_input:
            return {"error": "Provide either text or texts."}

        translation = runtime.translate(
            job_input["text"],
            source_language,
            target_language,
        )
        return {
            "translation": translation,
            "source_language": source_language,
            "target_language": target_language,
        }

    except ValueError as exc:
        logger.warning("Invalid IndicTrans2 request: %s", exc)
        return {"error": str(exc)}
    except Exception as exc:
        logger.exception("IndicTrans2 RunPod job failed (%s): %s", type(exc).__name__, exc)
        return {"error": "GPU translation failed.", "error_type": type(exc).__name__, "error_detail": str(exc)[:1500]}


if __name__ == "__main__":
    runpod.serverless.start({"handler": handler})
