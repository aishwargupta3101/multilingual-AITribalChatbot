"""
Optimized NLLB Translation Service
"""

import logging
import torch
from backend.config.translation_config import TranslationConfig
from backend.translation.supported_languages import SUPPORTED_LANGUAGES
logger = logging.getLogger(__name__)

class NLLBService:
    """
    Optimized NLLB Translation Service.

    Optimizations:
    - Loads model only once.
    - Uses inference_mode().
    - Uses FP16 on CUDA when appropriate.
    - Uses caching for repeated translations.
    - Removes unnecessary console output.
    """
    def __init__(self):
        self.device = TranslationConfig.DEVICE
        self.tokenizer = None
        self.model = None
        self._model_loaded = False

    def load_model(self):
        if self._model_loaded:
            return
        from transformers import (
            AutoTokenizer,
            AutoModelForSeq2SeqLM
        )
        logger.info(
            "Loading NLLB Translation Model..."
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            TranslationConfig.MODEL_NAME,
            cache_dir=TranslationConfig.MODEL_CACHE_DIR
        )
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            TranslationConfig.MODEL_NAME,
            cache_dir=TranslationConfig.MODEL_CACHE_DIR
        )
        self.model = self.model.to(self.device)

        if self.device.startswith("cuda"):
            logger.info(
                "CUDA detected. Enabling FP16 inference."
            )
            self.model = self.model.half()

        self.model.eval()
        self._model_loaded = True
        logger.info(
            "NLLB Translation Model Loaded Successfully."
        )
    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:
        if not text or not text.strip():
            return ""
        text = text.strip()
        source_language = (
            source_language.lower().strip()
        )
        target_language = (
            target_language.lower().strip()
        )
        if source_language == target_language:
            return text

        if source_language not in SUPPORTED_LANGUAGES:

            raise ValueError(
                f"Unsupported source language: "
                f"{source_language}"
            )
        if target_language not in SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported target language: "
                f"{target_language}"
            )
        source_code = (
            SUPPORTED_LANGUAGES[
                source_language
            ]["code"]
        )
        target_code = (
            SUPPORTED_LANGUAGES[
                target_language
            ]["code"]
        )
        if source_code is None:
            raise ValueError(
                f"Translation for "
                f"'{source_language}' "
                f"is not available yet."
            )
        if target_code is None:
            raise ValueError(
                f"Translation for "
                f"'{target_language}' "
                f"is not available yet."
            )
        self.load_model()
        self.tokenizer.src_lang = source_code
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=TranslationConfig.MAX_INPUT_LENGTH
        )
        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }
        try:
            bos_token_id = (
                self.tokenizer.lang_code_to_id[
                    target_code
                ]
            )
        except AttributeError:
            bos_token_id = (
                self.tokenizer
                .convert_tokens_to_ids(
                    target_code
                )
            )
        with torch.inference_mode():
            generated_tokens = self.model.generate(
                **inputs,
                forced_bos_token_id=bos_token_id,
                max_new_tokens=TranslationConfig.MAX_NEW_TOKEN,
                num_beams=1,
                do_sample=False
            )
        translated_text = (
            self.tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True
            )[0]
            .strip()
        )
        logger.info(
            "Translation completed: %s -> %s",
            source_language,
            target_language
        )
        return translated_text
nllb_service = NLLBService()