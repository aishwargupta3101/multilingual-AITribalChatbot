
"""
Modal GPU service for IndicTrans2.

Supports:
- English -> Indic
- Indic -> English
- Indic -> Indic

The service loads one model at a time and reuses it
for subsequent requests in the same Modal container.
"""

import os
import gc
import time
import hmac
import logging
import threading
from pathlib import Path
from functools import lru_cache

import modal
APP_NAME = "tribal-indictrans-gpu"
SECRET_NAME = "tribal-indictrans-auth"

app = modal.App(APP_NAME)

BASE_DIR = Path(__file__).resolve().parent

image = (
    modal.Image.debian_slim(python_version="3.11")
    # CUDA-enabled PyTorch; separate from your desktop CPU environment.
    .uv_pip_install(
        "torch==2.5.1",
        index_url="https://download.pytorch.org/whl/cu124",
    )
    # Only the dependencies needed by IndicTrans2.
    .uv_pip_install(
        requirements=[str(BASE_DIR / "requirements.txt")]
    )
    .env({
        "HF_HOME": "/root/.cache/huggingface",
        "TOKENIZERS_PARALLELISM": "false",
    })
)
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
        self.cache_dir = Path("/root/.cache/indictrans2")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        logging.info(
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

        self.tokenizer = AutoTokenizer.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir=str(self.cache_dir),
        )

        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            model_name,
            trust_remote_code=True,
            cache_dir=str(self.cache_dir),
            low_cpu_mem_usage=True,
        )

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

                processed_texts = self.processor.preprocess_batch(
                    batch_texts,
                    src_lang=source_code,
                    tgt_lang=target_code,
                )

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

                with self.torch.inference_mode():
                    generated_tokens = self.model.generate(
                        **inputs,
                        **generation_args,
                    )

                decoded = self.tokenizer.batch_decode(
                    generated_tokens,
                    skip_special_tokens=True,
                    clean_up_tokenization_spaces=True,
                )

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
@app.function(
    image=image,
    gpu="T4",
    secrets=[
        modal.Secret.from_name(SECRET_NAME)
    ],
    timeout=900,
    startup_timeout=900,
    memory=16384,
)
@modal.asgi_app()
def web_app():

    from fastapi import FastAPI, HTTPException, Request
    from fastapi.concurrency import run_in_threadpool

    api = FastAPI(
        title="Tribal IndicTrans2 GPU Service",
        version="1.0.0",
    )

    runtime = IndicTransRuntime()

    def verify_authentication(request):
        expected_token = os.environ.get("TRIBAL_GPU_API_TOKEN")

        if not expected_token:
            raise HTTPException(
                status_code=503,
                detail="GPU service authentication is not configured.",
            )

        authorization = request.headers.get("Authorization", "")

        supplied_token = (
            authorization[7:].strip()
            if authorization.startswith("Bearer ")
            else ""
        )

        if not supplied_token or not hmac.compare_digest(
            supplied_token,
            expected_token,
        ):
            raise HTTPException(
                status_code=401,
                detail="Invalid or missing authentication token.",
            )

    @api.get("/health")
    async def health(request: Request):
        verify_authentication(request)

        return {
            "status": "healthy",
            "service": "IndicTrans2 GPU",
            "device": str(runtime.device),
            "gpu": runtime.torch.cuda.get_device_name(0),
            "active_model": runtime.active_model_name,
        }

    @api.post("/translate")
    async def translate(request: Request):
        verify_authentication(request)

        try:
            data = await request.json()

            source_language = data.get("source_language")
            target_language = data.get("target_language")

            if not source_language or not target_language:
                raise HTTPException(
                    status_code=400,
                    detail="source_language and target_language are required.",
                )

            started = time.perf_counter()

            if isinstance(data.get("texts"), list):
                translations = await run_in_threadpool(
                    runtime.translate_batch,
                    data["texts"],
                    source_language,
                    target_language,
                    data.get("batch_size", 8),
                )

                return {
                    "translations": translations,
                    "source_language": source_language,
                    "target_language": target_language,
                    "inference_ms": round(
                        (time.perf_counter() - started) * 1000,
                        2,
                    ),
                }

            if "text" not in data:
                raise HTTPException(
                    status_code=400,
                    detail="Provide either text or texts.",
                )

            translation = await run_in_threadpool(
                runtime.translate,
                data["text"],
                source_language,
                target_language,
            )

            return {
                "translation": translation,
                "source_language": source_language,
                "target_language": target_language,
                "inference_ms": round(
                    (time.perf_counter() - started) * 1000,
                    2,
                ),
            }

        except HTTPException:
            raise

        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail=str(exc),
            ) from exc

        except Exception as exc:
            logging.exception("IndicTrans2 translation failed.")

            raise HTTPException(
                status_code=500,
                detail="GPU translation failed. Check Modal logs.",
            ) from exc

    return api
