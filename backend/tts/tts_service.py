"""Provider-based TTS: gTTS where its installed language catalogue supports it,
with an optional local AI4Bharat Indic Parler-TTS fallback.

Manipuri/Santali dedicated routes are intentionally not replaced by this service.
"""
from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

from gtts import gTTS
from gtts.lang import tts_langs

logger = logging.getLogger(__name__)


class TTSService:
    PARLER_MODEL_ID = os.getenv("INDIC_PARLER_MODEL", "ai4bharat/indic-parler-tts")
    PARLER_ENABLED = os.getenv("ENABLE_INDIC_PARLER_TTS", "1").strip().lower() in {"1", "true", "yes", "on"}

    # Only aliases are declared here. A gTTS language is used only if the
    # installed gTTS catalogue confirms it at runtime (never guess provider codes).
    GTTS_CODES = {
        "english": "en", "hindi": "hi", "bengali": "bn", "gujarati": "gu",
        "kannada": "kn", "malayalam": "ml", "marathi": "mr", "nepali": "ne",
        "punjabi": "pa", "tamil": "ta", "telugu": "te", "urdu": "ur",
    }

    # Official Indic Parler-TTS language coverage from its model card.
    PARLER_LANGUAGES = {
        "assamese", "bengali", "bodo", "dogri", "english", "gujarati",
        "hindi", "kannada", "konkani", "maithili", "malayalam", "manipuri",
        "marathi", "nepali", "odia", "sanskrit", "santali", "sindhi",
        "tamil", "telugu", "urdu",
    }

    # Speaker prompts are model-card examples / recommended speakers.
    SPEAKERS = {
        "assamese": "Sita", "bengali": "Aditi", "bodo": "Maya", "dogri": "Karan",
        "english": "Mary", "gujarati": "Neha", "hindi": "Divya", "kannada": "Anu",
        "konkani": "Neha", "maithili": "Amrita", "malayalam": "Anjali",
        "manipuri": "Laishram", "marathi": "Sunita", "nepali": "Amrita",
        "odia": "Debjani", "sanskrit": "Aryan", "santali": "Maya",
        "sindhi": "Aditi", "tamil": "Jaya", "telugu": "Lalitha", "urdu": "Aditi",
    }

    def __init__(self):
        self._parler_model = None
        self._parler_tokenizer = None
        self._description_tokenizer = None
        self._device = None

    def _load_parler(self):
        if self._parler_model is not None:
            return
        try:
            import torch
            from parler_tts import ParlerTTSForConditionalGeneration
            from transformers import AutoTokenizer
        except ImportError as exc:
            raise RuntimeError(
                "Indic Parler-TTS dependencies are missing. Install the packages listed "
                "in tts_indic_requirements.txt and restart the backend."
            ) from exc

        self._device = "cuda:0" if torch.cuda.is_available() else "cpu"
        logger.info("Loading Indic Parler-TTS model %s on %s", self.PARLER_MODEL_ID, self._device)
        self._parler_model = ParlerTTSForConditionalGeneration.from_pretrained(
            self.PARLER_MODEL_ID
        ).to(self._device)
        self._parler_tokenizer = AutoTokenizer.from_pretrained(self.PARLER_MODEL_ID)
        self._description_tokenizer = AutoTokenizer.from_pretrained(
            self._parler_model.config.text_encoder._name_or_path
        )
        self._parler_model.eval()
        logger.info("Indic Parler-TTS model loaded successfully")

    def _generate_parler_wav(self, text: str, language: str, output_path: str) -> None:
        import soundfile as sf
        import torch

        self._load_parler()
        speaker = self.SPEAKERS.get(language, "Aditi")
        description = (
            f"{speaker} speaks clearly in {language}, at a moderate pace and pitch. "
            "The recording is very clear audio, with a close, natural voice and no background noise."
        )
        desc_inputs = self._description_tokenizer(description, return_tensors="pt").to(self._device)
        prompt_inputs = self._parler_tokenizer(text, return_tensors="pt").to(self._device)
        with torch.inference_mode():
            audio = self._parler_model.generate(
                input_ids=desc_inputs.input_ids,
                attention_mask=desc_inputs.attention_mask,
                prompt_input_ids=prompt_inputs.input_ids,
                prompt_attention_mask=prompt_inputs.attention_mask,
            )
        audio_array = audio.detach().cpu().numpy().squeeze()
        if audio_array.size == 0:
            raise RuntimeError("Indic Parler-TTS returned empty audio.")
        sf.write(output_path, audio_array, self._parler_model.config.sampling_rate, subtype="PCM_16")

    async def generate_speech(self, text: str, language: str = "english"):
        language = (language or "english").strip().lower().replace(" ", "_")
        text = (text or "").strip()
        if not text:
            return {"success": False, "error": "Text is empty."}
        if language in {"manipuri", "manipuri_mtei", "santali"}:
            return {
                "success": False,
                "error": f"Use the dedicated {language} TTS route; the generic TTS endpoint does not replace it.",
            }

        gtts_catalogue = tts_langs()
        gtts_code = self.GTTS_CODES.get(language)
        if gtts_code and gtts_code in gtts_catalogue:
            fd, audio_path = tempfile.mkstemp(suffix=".mp3")
            os.close(fd)
            try:
                logger.info("TTS provider=gTTS language=%s code=%s", language, gtts_code)
                await asyncio.to_thread(gTTS(text=text, lang=gtts_code, slow=False).save, audio_path)
                if not os.path.isfile(audio_path) or os.path.getsize(audio_path) == 0:
                    raise RuntimeError("gTTS generated an empty audio file.")
                return {"success": True, "audio_file": audio_path, "language": language, "format": "mp3", "provider": "gTTS"}
            except Exception as exc:
                logger.exception("gTTS failed for %s", language)
                try:
                    os.remove(audio_path)
                except OSError:
                    pass
                # If this language is covered by Parler, try that provider below.
                if not (self.PARLER_ENABLED and language in self.PARLER_LANGUAGES):
                    return {"success": False, "error": f"gTTS failed: {exc}"}

        if self.PARLER_ENABLED and language in self.PARLER_LANGUAGES:
            fd, audio_path = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
            try:
                logger.info("TTS provider=Indic-Parler-TTS language=%s", language)
                await asyncio.to_thread(self._generate_parler_wav, text, language, audio_path)
                if not os.path.isfile(audio_path) or os.path.getsize(audio_path) == 0:
                    raise RuntimeError("Indic Parler-TTS generated an empty audio file.")
                return {"success": True, "audio_file": audio_path, "language": language, "format": "wav", "provider": "Indic-Parler-TTS"}
            except Exception as exc:
                logger.exception("Indic Parler-TTS failed for %s", language)
                try:
                    os.remove(audio_path)
                except OSError:
                    pass
                return {"success": False, "error": f"Indic Parler-TTS failed for {language}: {exc}"}

        return {
            "success": False,
            "error": (
                f"No configured TTS provider supports '{language}'. "
                "Check the gTTS language catalogue or enable Indic Parler-TTS."
            ),
        }


tts_service = TTSService()
