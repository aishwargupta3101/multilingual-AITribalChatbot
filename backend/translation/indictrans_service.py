
"""
Optimized IndicTrans2 Translation Service
Supports English, Hindi, Manipuri Bengali, and Meitei Mayek.
"""
import gc
import logging
import threading
from functools import lru_cache
from pathlib import Path
import torch
from backend.config.translation_config import TranslationConfig

logger = logging.getLogger(__name__)

class IndicTransService:
    """Lazy-loaded, memory-conscious IndicTrans2 translation service."""

    LANGUAGE_CODES = {
        "english": "eng_Latn",
        "hindi": "hin_Deva",
        "manipuri": "mni_Beng",
        "manipuri_beng": "mni_Beng",
        "manipuri_bengali": "mni_Beng",
        "manipuri_mtei": "mni_Mtei",
        "manipuri_mayek": "mni_Mtei",
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
            self._processor = IndicProcessor(inference=True)
            self._active_model_name = model_name
            logger.info("IndicTrans2 model loaded: %s", model_name)

        except Exception:
            self._release_model()
            logger.exception("Failed to load IndicTrans2 model: %s", model_name)
            raise

    @classmethod
    def _validate_language(cls, language: str):
        """Validate supported IndicTrans2 languages."""
        if language not in cls.LANGUAGE_CODES:
            raise ValueError(f"IndicTrans2 does not support language: {language}")

    @lru_cache(maxsize=512)
    def _translate_cached(self, text: str, source_language: str, target_language: str) -> str:
        return self._translate(text, source_language, target_language)

    def _translate(self, text: str, source_language: str, target_language: str) -> str:
        self._validate_language(source_language)
        self._validate_language(target_language)

        if source_language == target_language:
            return text

        model_name = self._get_model_name(source_language, target_language)
        source_code = self.LANGUAGE_CODES[source_language]
        target_code = self.LANGUAGE_CODES[target_language]

        with self._lock:
            self._load_model(model_name)

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
                "max_new_tokens": TranslationConfig.MAX_NEW_TOKEN,
                "num_beams": 1,
                "do_sample": False,
                "use_cache": True
            }

            with torch.inference_mode():
                generated_tokens = self._model.generate(**inputs, **generation_args)

            decoded = self._tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True
            )
            raw_output = decoded[0].strip()
            processed_output = self._processor.postprocess_batch(decoded)[0].strip()
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

            return result

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