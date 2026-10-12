
import gc
import logging
import threading
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from backend.config.translation_config import TranslationConfig

logger = logging.getLogger(__name__)

class ManipuriBengaliService:
    MODEL_NAME = "abhishek2475/mb-Hindi-to-manipuri"
    MAX_NEW_TOKENS = 128
    NUM_BEAMS = 4
    REPETITION_PENALTY = 1.5
    NO_REPEAT_NGRAM_SIZE = 3
    BENGALI_THRESHOLD = 0.65

    def __init__(self):
        self.device = torch.device(TranslationConfig.DEVICE)
        self.tokenizer = None
        self.model = None
        self.lock = threading.RLock()

    def _load_model(self):
        if self.model is not None and self.tokenizer is not None:
            return
        logger.info("Loading Manipuri Bengali model...")
        tokenizer = AutoTokenizer.from_pretrained(
            self.MODEL_NAME,
            cache_dir=str(TranslationConfig.INDICTRANS_CACHE_DIR)
        )
        model = AutoModelForSeq2SeqLM.from_pretrained(
            self.MODEL_NAME,
            cache_dir=str(TranslationConfig.INDICTRANS_CACHE_DIR)
        )
        model.to(self.device)
        model.eval()
        self.tokenizer = tokenizer
        self.model = model
        logger.info("Manipuri Bengali model loaded successfully.")

    @staticmethod
    def _bengali_ratio(text):
        letters = [char for char in text if char.isalpha()]
        if not letters:
            return 0.0
        bengali = sum(0x0980 <= ord(char) <= 0x09FF for char in letters)
        return bengali / len(letters)

    @staticmethod
    def _is_repetitive(text):
        words = text.lower().split()
        if len(words) < 8:
            return False
        for size in range(2, min(7, len(words) // 2) + 1):
            for start in range(len(words) - 2 * size + 1):
                if words[start:start + size] == words[start + size:start + 2 * size]:
                    return True
        return False

    def _validate_output(self, result, source_text):
        if not result:
            raise ValueError("Manipuri Bengali model returned an empty translation.")
        if result.strip().lower() == source_text.strip().lower():
            raise ValueError("Model returned the original text without translation.")
        ratio = self._bengali_ratio(result)
        if ratio < self.BENGALI_THRESHOLD:
            raise ValueError(
                f"Output is not predominantly Bengali script. Bengali ratio: {ratio:.2f}"
            )
        if self._is_repetitive(result):
            raise ValueError("Repetitive translation detected.")
        return result.strip()

    def translate_hindi(self, text):
        if not text or not text.strip():
            return ""
        source_text = text.strip()
        with self.lock:
            self._load_model()
            inputs = self.tokenizer(
                source_text,
                return_tensors="pt",
                truncation=True,
                max_length=TranslationConfig.MAX_INPUT_LENGTH
            )
            inputs = {
                key: value.to(self.device)
                for key, value in inputs.items()
            }
            with torch.inference_mode():
                output = self.model.generate(
                    **inputs,
                    max_new_tokens=self.MAX_NEW_TOKENS,
                    num_beams=self.NUM_BEAMS,
                    do_sample=False,
                    repetition_penalty=self.REPETITION_PENALTY,
                    no_repeat_ngram_size=self.NO_REPEAT_NGRAM_SIZE,
                    early_stopping=False
                )
            result = self.tokenizer.decode(
                output[0],
                skip_special_tokens=True
            ).strip()
            result = self._validate_output(result, source_text)
            logger.info("Hindi-to-Manipuri translation completed.")
            return result

    def translate_english(self, text):
        if not text or not text.strip():
            return ""
        from backend.translation.indictrans_service import indictrans_service
        hindi = indictrans_service.translate(
            text.strip(),
            "english",
            "hindi"
        )
        if not hindi or not hindi.strip():
            raise ValueError(
                "English-to-Hindi pivot translation returned empty text."
            )
        return self.translate_hindi(hindi)

    def translate(self, text, source_language="hindi"):
        if not text or not text.strip():
            return ""
        source = source_language.lower().strip()
        if source in ("hindi", "hi", "hin"):
            return self.translate_hindi(text)
        if source in ("english", "en", "eng"):
            return self.translate_english(text)
        raise ValueError(f"Unsupported source language: {source_language}")

    def release_model(self):
        with self.lock:
            self.model = None
            self.tokenizer = None
            gc.collect()
            if self.device.type == "cuda" and torch.cuda.is_available():
                torch.cuda.empty_cache()

manipuri_bengali_service = ManipuriBengaliService()