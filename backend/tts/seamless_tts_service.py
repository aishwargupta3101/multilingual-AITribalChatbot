"""
SeamlessM4T Text-to-Speech Service
"""

import logging
import os
import uuid

import soundfile as sf
import torch
from transformers import AutoProcessor, SeamlessM4Tv2Model
logger = logging.getLogger(__name__)


class SeamlessTTSService:
    LANGUAGE_CODES = {
        "english": "eng",
        "hindi": "hin",
    }

    def __init__(self):
        logger.info("Loading SeamlessM4T TTS Model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained(
            "facebook/seamless-m4t-v2-large"
        )
        self.model = SeamlessM4Tv2Model.from_pretrained(
            "facebook/seamless-m4t-v2-large"
        ).to(self.device)
        os.makedirs("generated_audio", exist_ok=True)
        logger.info("SeamlessM4T Loaded Successfully.")

    def text_to_speech(self, text: str, language: str) -> str:
        language = language.lower()
        if language not in self.LANGUAGE_CODES:
            raise ValueError(
                f"TTS not supported for {language}"
            )
        tgt_lang = self.LANGUAGE_CODES[language]
        inputs = self.processor(
            text=text,
            src_lang="eng",
            return_tensors="pt",
        )
        inputs = {
            k: v.to(self.device)
            for k, v in inputs.items()
        }
        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                tgt_lang=tgt_lang,
                generate_speech=True,
            )
        if isinstance(output, tuple):
            audio = output[0]
        elif hasattr(output, "audio"):
            audio = output.audio
        else:
            audio = output
        if not isinstance(audio, torch.Tensor):
            raise RuntimeError(
                f"Unsupported output type from generate(): {type(output)}"
            )
        audio = audio.detach().cpu().numpy().squeeze()
        filename = f"{uuid.uuid4()}.wav"
        filepath = os.path.join(
            "generated_audio",
            filename,
        )
        sf.write(
            filepath,
            audio,
            16000,
        )
        logger.info(f"TTS Audio Saved: {filepath}")
        return filepath

seamless_tts_service = SeamlessTTSService()