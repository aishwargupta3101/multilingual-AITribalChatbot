
"""
Optimized IndicTrans2 Translation Service
Supports English, Hindi, Manipuri Bengali, and Meitei Mayek.
"""
import gc
import logging
import os
import threading
import time
from functools import lru_cache
from pathlib import Path
import torch
from backend.config.translation_config import TranslationConfig

logger = logging.getLogger(__name__)

class IndicTransService:
    """Lazy-loaded IndicTrans2 service with optional CPU INT8 inference."""

    LANGUAGE_CODES = {
        "english": "eng_Latn",
        "hindi": "hin_Deva",
        "manipuri": "mni_Beng",
        "manipuri_beng": "mni_Beng",
        "manipuri_bengali": "mni_Beng",
        "manipuri_mtei": "mni_Mtei",
        "manipuri_mayek": "mni_Mtei",
        # IndicTrans2 language/script codes for the tested language set.
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
        "as": "assamese", "asm": "assamese",
        "bn": "bengali", "ben": "bengali",
        "brx": "bodo", "doi": "dogri",
        "gu": "gujarati", "guj": "gujarati",
        "kn": "kannada", "kan": "kannada",
        "ks": "kashmiri", "kas": "kashmiri",
        "kas_deva": "kashmiri_deva",
        "gom": "konkani", "mai": "maithili",
        "ml": "malayalam", "mal": "malayalam",
        "mr": "marathi", "mar": "marathi",
        "ne": "nepali", "npi": "nepali",
        "or": "odia", "ory": "odia",
        "pa": "punjabi", "pan": "punjabi",
        "sa": "sanskrit", "san": "sanskrit",
        "sd": "sindhi", "snd": "sindhi",
        "snd_deva": "sindhi_deva",
        "ta": "tamil", "tam": "tamil",
        "te": "telugu", "tel": "telugu",
        "ur": "urdu",
        "sat": "santali", "sat_olck": "santali",
    }

    def __init__(self):
        self.device = torch.device(TranslationConfig.DEVICE)
        self._model = None
        self._tokenizer = None
        self._processor = None
        self._active_model_name = None
        self._lock = threading.RLock()

    @classmethod
    def normalize_language(cls, language: str) -> str:
        """Normalize language names and aliases."""
        if not language:
            raise ValueError("Language cannot be empty.")
        language = language.lower().strip().replace("-", "_").replace(" ", "_")
        return cls.LANGUAGE_ALIASES.get(language, language)

    def _get_model_name(self, source_language: str, target_language: str) -> str:
        """Select the appropriate IndicTrans2 model."""
        if source_language == "english":
            return TranslationConfig.INDICTRANS_EN_INDIC_MODEL
        if target_language == "english":
            return TranslationConfig.INDICTRANS_INDIC_EN_MODEL
        return TranslationConfig.INDICTRANS_INDIC_INDIC_MODEL

    def _release_model(self):
        """Release the currently loaded model to limit memory use."""
        self._model = None
        self._tokenizer = None
        self._processor = None
        self._active_model_name = None
        gc.collect()
        if self.device.type == "cuda":
            torch.cuda.empty_cache()

    def _load_model(self, model_name: str):
        """Load only the model required for the current translation."""
        if self._active_model_name == model_name and self._model is not None:
            return
        load_started = time.perf_counter()
        previous_model = self._active_model_name
        logger.info("IndicTrans2 model switch | from=%s | to=%s", previous_model, model_name)
        self._release_model()
        try:
            from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
            from IndicTransToolkit import IndicProcessor

            logger.info("Loading IndicTrans2 model: %s", model_name)
            cache_dir = Path(TranslationConfig.INDICTRANS_CACHE_DIR)
            cache_dir.mkdir(parents=True, exist_ok=True)

            self._tokenizer = AutoTokenizer.from_pretrained(
                model_name,
                trust_remote_code=True,
                cache_dir=str(cache_dir)
            )
            self._model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name,
                trust_remote_code=True,
                cache_dir=str(cache_dir),
                low_cpu_mem_usage=True
            )
            self._model.to(self.device)

            if self.device.type == "cuda" and TranslationConfig.USE_FP16:
                self._model.half()

            self._model.eval()

            # Optional CPU dynamic INT8 quantization. It keeps the same model
            # architecture and generation settings while reducing Linear-layer
            # weight size. If the installed PyTorch/model combination does not
            # support it, safely retain the original FP32 model.
            use_cpu_int8 = (
                self.device.type == "cpu"
                and os.getenv("TRIBAL_INDIC_INT8", "1").strip().lower()
                not in {"0", "false", "no", "off"}
            )
            if use_cpu_int8:
                try:
                    quantize_dynamic = torch.ao.quantization.quantize_dynamic
                    self._model = quantize_dynamic(
                        self._model,
                        {torch.nn.Linear},
                        dtype=torch.qint8,
                        inplace=False
                    )
                    self._model.eval()
                    logger.info(
                        "IndicTrans2 CPU dynamic INT8 quantization enabled: %s",
                        model_name
                    )
                except Exception:
                    logger.exception(
                        "IndicTrans2 CPU INT8 quantization unavailable; "
                        "continuing with FP32 model: %s",
                        model_name
                    )

            self._processor = IndicProcessor(inference=True)
            self._active_model_name = model_name
            logger.info("IndicTrans2 model loaded: %s | seconds=%.3f", model_name, time.perf_counter() - load_started)

        except Exception:
            self._release_model()
            logger.exception("Failed to load IndicTrans2 model: %s | seconds=%.3f", model_name, time.perf_counter() - load_started)
            raise

    @classmethod
    def _validate_language(cls, language: str):
        """Validate supported IndicTrans2 languages."""
        if language not in cls.LANGUAGE_CODES:
            raise ValueError(f"IndicTrans2 does not support language: {language}")

    @lru_cache(maxsize=512)
    def _translate_cached(self, text: str, source_language: str, target_language: str) -> str:
        return self._translate(text, source_language, target_language)

    @staticmethod
    def _get_max_new_tokens(inputs) -> int:
        """
        Scale the output budget to the tokenized input length.

        The previous fixed 128-token limit could cut off longer translations.
        Keep the existing minimum, with a conservative upper bound.
        """
        input_tokens = int(inputs["input_ids"].shape[-1])
        configured_limit = int(TranslationConfig.MAX_NEW_TOKEN)
        adaptive_limit = int(input_tokens * 1.5) + 32
        return min(384, max(configured_limit, adaptive_limit))

    def _translate(self, text: str, source_language: str, target_language: str) -> str:
        self._validate_language(source_language)
        self._validate_language(target_language)

        if source_language == target_language:
            return text

        model_name = self._get_model_name(source_language, target_language)
        source_code = self.LANGUAGE_CODES[source_language]
        target_code = self.LANGUAGE_CODES[target_language]

        request_started = time.perf_counter()
        with self._lock:
            self._load_model(model_name)
            ready_at = time.perf_counter()

            processed_text = self._processor.preprocess_batch(
                [text],
                src_lang=source_code,
                tgt_lang=target_code
            )
            inputs = self._tokenizer(
                processed_text,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=TranslationConfig.MAX_INPUT_LENGTH
            )
            inputs = {key: value.to(self.device) for key, value in inputs.items()}

            generation_args = {
                "max_new_tokens": self._get_max_new_tokens(inputs),
                "num_beams": 1,
                "do_sample": False,
                "use_cache": True
            }

            generation_started = time.perf_counter()
            with torch.inference_mode():
                generated_tokens = self._model.generate(**inputs, **generation_args)
            generation_seconds = time.perf_counter() - generation_started

            decoded = self._tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            raw_output = decoded[0].strip()
            # Pass the target language so IndicTransToolkit can apply target-specific
            # post-processing instead of relying on its default language behavior.
            processed_output = self._processor.postprocess_batch(
                decoded, lang=target_code
            )[0].strip()
            print("\n" + "=" * 60)
            print("SOURCE LANGUAGE:", source_code)
            print("TARGET LANGUAGE:", target_code)
            print("RAW MODEL OUTPUT:", raw_output)
            print("POSTPROCESSED OUTPUT:", processed_output)
            print("=" * 60)
            logger.info("IndicTrans2 raw output: %s", raw_output)
            logger.info("IndicTrans2 processed output: %s", processed_output)

            result = processed_output
            if not result:
                raise ValueError("IndicTrans2 returned an empty translation.")
            logger.info("IndicTrans2 timing | %s -> %s | chars=%d | wait_and_load=%.3fs | generation=%.3fs | total=%.3fs", source_language, target_language, len(text), ready_at - request_started, generation_seconds, time.perf_counter() - request_started)

            return result


    def _translate_batch(self, texts, source_language: str, target_language: str):
        """Translate a small batch with one model.generate call, preserving input order."""
        self._validate_language(source_language)
        self._validate_language(target_language)
        if source_language == target_language:
            return list(texts)

        model_name = self._get_model_name(source_language, target_language)
        source_code = self.LANGUAGE_CODES[source_language]
        target_code = self.LANGUAGE_CODES[target_language]

        request_started = time.perf_counter()
        with self._lock:
            self._load_model(model_name)
            ready_at = time.perf_counter()
            processed_texts = self._processor.preprocess_batch(
                list(texts),
                src_lang=source_code,
                tgt_lang=target_code
            )
            inputs = self._tokenizer(
                processed_texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=TranslationConfig.MAX_INPUT_LENGTH
            )
            inputs = {key: value.to(self.device) for key, value in inputs.items()}
            generation_args = {
                "max_new_tokens": self._get_max_new_tokens(inputs),
                "num_beams": 1,
                "do_sample": False,
                "use_cache": True
            }
            generation_started = time.perf_counter()
            with torch.inference_mode():
                generated_tokens = self._model.generate(**inputs, **generation_args)
            generation_seconds = time.perf_counter() - generation_started

            decoded = self._tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            outputs = self._processor.postprocess_batch(decoded, lang=target_code)
            results = [str(output or "").strip() for output in outputs]
            if len(results) != len(texts):
                raise ValueError(
                    f"IndicTrans2 batch size mismatch: expected {len(texts)}, got {len(results)}"
                )
            if any(not result for result in results):
                raise ValueError("IndicTrans2 returned an empty translation in a batch.")
            logger.info("IndicTrans2 batch timing | %s -> %s | items=%d | wait_and_load=%.3fs | generation=%.3fs | total=%.3fs", source_language, target_language, len(texts), ready_at - request_started, generation_seconds, time.perf_counter() - request_started)
            return results

    def translate_batch(
        self,
        texts,
        source_language: str,
        target_language: str,
        batch_size: int = 8
    ):
        """Batch independent text fragments without changing the single-text API."""
        if not texts:
            return []
        source_language = self.normalize_language(source_language)
        target_language = self.normalize_language(target_language)
        self._validate_language(source_language)
        self._validate_language(target_language)
        cleaned = [str(text or "").strip() for text in texts]
        results = [""] * len(cleaned)

        # Retain blank fragments and same-language behavior in their original positions.
        active_indices = [
            index for index, value in enumerate(cleaned)
            if value and source_language != target_language
        ]
        for index, value in enumerate(cleaned):
            if value and source_language == target_language:
                results[index] = value

        if not active_indices:
            return results

        # Very small batches avoid excessive padding and limit memory use.
        batch_size = max(1, min(int(batch_size), 8))
        for start in range(0, len(active_indices), batch_size):
            indices = active_indices[start:start + batch_size]
            batch = [cleaned[index] for index in indices]
            translated = self._translate_batch(batch, source_language, target_language)
            for index, value in zip(indices, translated):
                results[index] = value
        return results

    def translate(self, text: str, source_language: str, target_language: str) -> str:
        """Translate text between supported languages."""
        if not text or not text.strip():
            return ""

        text = text.strip()
        source_language = self.normalize_language(source_language)
        target_language = self.normalize_language(target_language)

        self._validate_language(source_language)
        self._validate_language(target_language)

        if source_language == target_language:
            return text

        return self._translate_cached(text, source_language, target_language)

    def clear_cache(self):
        """Clear cached translations."""
        self._translate_cached.cache_clear()
        logger.info("IndicTrans2 translation cache cleared.")

indictrans_service = IndicTransService()