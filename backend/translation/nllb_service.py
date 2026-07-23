"""
NLLB Translation Service
"""
import logging
import torch
from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM
)
from backend.config.translation_config import TranslationConfig
from backend.translation.supported_languages import SUPPORTED_LANGUAGES

logger = logging.getLogger(__name__)
class NLLBService:
    """
    NLLB Translation Service
    """
    def __init__(self):
        logger.info("Loading NLLB Translation Model...")
        self.device = TranslationConfig.DEVICE
        self.tokenizer = AutoTokenizer.from_pretrained(
            TranslationConfig.MODEL_NAME,
            cache_dir=TranslationConfig.MODEL_CACHE_DIR
        )
        self.model = AutoModelForSeq2SeqLM.from_pretrained(
            TranslationConfig.MODEL_NAME,
            cache_dir=TranslationConfig.MODEL_CACHE_DIR
        ).to(self.device)
        logger.info("NLLB Model Loaded Successfully.")
    def translate(
            self,
            text: str,
            source_language: str,
            target_language: str

    ) -> str:
        """
        Translate text using NLLB.
        """
        if not text.strip():
            return ""
        source_language = source_language.lower()
        target_language = target_language.lower()
        if source_language == target_language:
            return text
        if source_language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported source language: {source_language}")
        if target_language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported target language: {target_language}")
        source_code = SUPPORTED_LANGUAGES[source_language]["code"]
        target_code = SUPPORTED_LANGUAGES[target_language]["code"]
        if source_code is None:
            raise ValueError(
                f"{source_language} is not supported by NLLB."
            )
        if target_code is None:
            raise ValueError(
                f"{target_language} is not supported by NLLB."
            )
        self.tokenizer.src_lang = source_code
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=TranslationConfig.MAX_INPUT_LENGTH
        )
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            try:
                bos_token_id = self.tokenizer.lang_code_to_id[target_code]
            except AttributeError:
                bos_token_id = self.tokenizer.convert_tokens_to_ids(
                    target_code
                )

        generated_tokens = self.model.generate(
            **inputs,
            forced_bos_token_id=bos_token_id,
            max_new_tokens=TranslationConfig.MAX_NEW_TOKEN
        )
        translated_text = self.tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True
        )[0]
        logger.info(
            f"Translation completed: { translated_text}"
        )
        return translated_text

nllb_service = NLLBService()