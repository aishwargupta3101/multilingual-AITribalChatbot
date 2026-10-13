"""
Optimized CTranslate2 INT8 NLLB Translation Service.
"""
import logging
from functools import lru_cache
import threading
import ctranslate2
from transformers import AutoTokenizer
from backend.config.translation_config import TranslationConfig
from backend.translation.supported_languages import SUPPORTED_LANGUAGES
import os
from huggingface_hub import snapshot_download
logger = logging.getLogger(__name__)

class NLLBService:
    """
    Fast NLLB translation using the existing CTranslate2 INT8 model.
    Keeps the public translate() interface unchanged.
    """
    LANGUAGE_ALIASES = {
        "en": "english",
        "eng": "english",
        "eng_latn": "english",
        "hi": "hindi",
        "hin": "hindi",
        "hin_deva": "hindi",
        "mni": "manipuri",
        "meitei": "manipuri",
        "mni_beng": "manipuri",
        "manipuri_beng": "manipuri",
        "manipuri_bengali": "manipuri",
        "manipuri": "manipuri",
        "mni_mtei": "manipuri_mtei",
        "manipuri_mtei": "manipuri_mtei",
        "meitei_mayek": "manipuri_mtei",
        "tai khamti": "tai_khamti"
    }
    def __init__(self):
        self.model_path = str(
            TranslationConfig.MODEL_CACHE_DIR
            / "nllb-200-distilled-600M-int8"
        )
        self.tokenizer = None
        self.translator = None
        self._model_loaded = False
        self._model_lock = threading.Lock()
        self._translation_lock = threading.Lock()
    @classmethod
    def normalize_language(cls, language: str) -> str:
        language = str(language or "english").lower().strip().replace("-", "_")
        return cls.LANGUAGE_ALIASES.get(language, language)
    def load_model(self):
        if self._model_loaded:
            return
        with self._model_lock:
            if self._model_loaded:
                return
            logger.info("Loading CTranslate2 INT8 NLLB model...")
            model_file = os.path.join(self.model_path, "model.bin")
            if not os.path.isfile(model_file):
                hf_token = os.getenv("HF_TOKEN")
                if not hf_token:
                    raise RuntimeError(
                        "HF_TOKEN is required to download the private NLLB model."
                    )
                logger.info("Downloading private CTranslate2 NLLB model...")
                snapshot_download(
                    repo_id="Ass123456/tribal-nllb-ct2-int8",
                    local_dir=self.model_path,
                    token=hf_token,
                )
            if not os.path.isfile(model_file):
                raise FileNotFoundError(
                    f"CTranslate2 model file is missing: {model_file}"
                )
            self.tokenizer = AutoTokenizer.from_pretrained(
                TranslationConfig.MODEL_NAME,
                cache_dir=TranslationConfig.MODEL_CACHE_DIR
            )
            self.translator = ctranslate2.Translator(
                self.model_path,
                device="cpu",
                compute_type="int8"
            )
            self._model_loaded = True
            logger.info("CTranslate2 INT8 NLLB model loaded successfully.")
    def _get_language_code(self, language: str) -> str:
        language = self.normalize_language(language)
        if language not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Unsupported language: {language}")
        language_config = SUPPORTED_LANGUAGES[language]
        code = (
            language_config.get("code")
            or language_config.get("translation_code")
        )
        if not code:
            raise ValueError(
                f"Translation for '{language}' is not available yet."
            )
        return code
    def _encode_source(self, text: str, source_code: str):
        self.tokenizer.src_lang = source_code
        input_ids = self.tokenizer.encode(
            text,
            add_special_tokens=True,
            truncation=True,
            max_length=TranslationConfig.MAX_INPUT_LENGTH
        )
        return self.tokenizer.convert_ids_to_tokens(input_ids)
    def _target_prefix(self, target_code: str):
        target_id = self.tokenizer.convert_tokens_to_ids(target_code)
        if target_id is None or target_id == self.tokenizer.unk_token_id:
            if hasattr(self.tokenizer, "lang_code_to_id"):
                target_id = self.tokenizer.lang_code_to_id.get(target_code)
        if target_id is None:
            raise ValueError(
                f"Unsupported NLLB target language code: {target_code}"
            )
        return [self.tokenizer.convert_ids_to_tokens([target_id])[0]]
    def _translate_cached(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:
        self.load_model()
        source_code = self._get_language_code(source_language)
        target_code = self._get_language_code(target_language)
        with self._translation_lock:
            source_tokens = self._encode_source(text, source_code)
            target_prefix = self._target_prefix(target_code)

            results = self.translator.translate_batch(
                [source_tokens],
                target_prefix=[target_prefix],
                beam_size=1,
                max_decoding_length=min(160, TranslationConfig.MAX_NEW_TOKEN),
                return_scores=False
            )
            hypothesis = results[0].hypotheses[0]
            translated_ids = self.tokenizer.convert_tokens_to_ids(hypothesis)
            translated_text = self.tokenizer.decode(
                translated_ids,
                skip_special_tokens=True
            ).strip()
        if not translated_text:
            raise ValueError(
                f"CTranslate2 returned an empty translation for "
                f"{source_language} -> {target_language}"
            )
        return translated_text
    @lru_cache(maxsize=1000)
    def _translate_cached_with_cache(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:
        return self._translate_cached(
            text,
            source_language,
            target_language
        )
    @staticmethod
    def _split_long_text(text: str, max_chars: int = 320):
        """Split long text at paragraph/sentence/word boundaries without dropping text."""
        import re
        text = str(text or "").strip()
        if not text:
            return []
        chunks = []
        paragraphs = re.split(r"\n\s*\n", text)
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if not paragraph:
                continue
            sentences = re.split(r"(?<=[.!?])\s+", paragraph)
            current = ""
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                if len(sentence) > max_chars:
                    words = sentence.split()
                    for word in words:
                        candidate = f"{current} {word}".strip()
                        if current and len(candidate) > max_chars:
                            chunks.append(current)
                            current = word
                        else:
                            current = candidate
                    continue
                candidate = f"{current} {sentence}".strip()
                if current and len(candidate) > max_chars:
                    chunks.append(current)
                    current = sentence
                else:
                    current = candidate
            if current:
                chunks.append(current)
        return chunks

    def translate(
        self,
        text: str,
        source_language: str,
        target_language: str
    ) -> str:
        if not text or not text.strip():
            return ""
        text = text.strip()
        source_language = self.normalize_language(source_language)
        target_language = self.normalize_language(target_language)
        if source_language == target_language:
            return text
        try:
            if source_language == "english" and target_language == "manipuri":
                chunks = self._split_long_text(text, max_chars=320)
                if len(chunks) > 1:
                    translated_chunks = []
                    for index, chunk in enumerate(chunks, start=1):
                        translated_chunks.append(
                            self._translate_cached_with_cache(
                                chunk, source_language, target_language
                            )
                        )
                    translated_text = "\n\n".join(translated_chunks).strip()
                    logger.info(
                        "Long Manipuri translation chunking | Source chars: %s | Chunks: %s",
                        len(text), len(chunks)
                    )
                else:
                    translated_text = self._translate_cached_with_cache(
                        text, source_language, target_language
                    )
            else:
                translated_text = self._translate_cached_with_cache(
                    text, source_language, target_language
                )
            logger.info(
                "Translation completed: %s -> %s",
                source_language,
                target_language
            )
            return translated_text
        except Exception:
            logger.exception(
                "Translation failed: %s -> %s",
                source_language,
                target_language
            )
            raise
    def clear_cache(self):
        self._translate_cached_with_cache.cache_clear()
        logger.info("NLLB translation cache cleared.")

nllb_service = NLLBService()
