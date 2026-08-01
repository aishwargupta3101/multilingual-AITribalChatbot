"""
Temporary XTTS Service

NOTE:
This currently uses SeamlessM4T as a temporary backend for TTS.
In Phase 8 (Fine-Tuning), replace the model loading with Coqui XTTS v2
without changing the rest of the project.
"""

import logging
import os
import uuid
import soundfile as sf
import torch
from transformers import AutoProcessor, SeamlessM4Tv2Model
logger = logging.getLogger(__name__)

class XTTSService:

    LANGUAGE_CODES = {
        "english": "eng",
        "hindi": "hin",
    }
    FUTURE_LANGUAGES = {
        "manipuri",
        "monpa",
        "tai khamti",
        "tai-khamti",
    }
    def __init__(self):
        logger.info("Loading Temporary XTTS Service (SeamlessM4T)...")

        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.processor = AutoProcessor.from_pretrained(
            "facebook/seamless-m4t-v2-large"
        )
        self.model = SeamlessM4Tv2Model.from_pretrained(
            "facebook/seamless-m4t-v2-large"
        ).to(self.device)
        os.makedirs("generated_audio", exist_ok=True)
        logger.info("Temporary XTTS Service Loaded Successfully.")
    def text_to_speech(self, text: str, language: str) -> str:

        language = language.lower().strip()
        if language in self.FUTURE_LANGUAGES:
            raise NotImplementedError(
                f"TTS for '{language}' is not available yet. "
                "It will be added after XTTS fine-tuning."
            )
        if language not in self.LANGUAGE_CODES:
            raise ValueError(
                f"Unsupported language: {language}"
            )
        tgt_lang = self.LANGUAGE_CODES[language]
        inputs = self.processor(
            text=text,
            src_lang="eng",
            return_tensors="pt",
        )
        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
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
                f"Unsupported output type: {type(output)}"
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
_xtts_service = None

def get_xtts_service():
    global _xtts_service
    if _xtts_service is None:
        _xtts_service = XTTSService()
    return _xtts_service