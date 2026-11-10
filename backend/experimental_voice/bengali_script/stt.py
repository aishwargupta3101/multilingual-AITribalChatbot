
"""
Experimental Manipuri STT — Bengali Script

This module is isolated from the production speech service.
It does not modify or replace the existing Whisper implementation.
"""

import logging
from pathlib import Path
from typing import Any
from faster_whisper import WhisperModel
logger = logging.getLogger(__name__)

class BengaliScriptSTT:
    """
    Experimental speech-to-text pipeline.

    The model's detected language and raw transcription are preserved
    for evaluation. We do not force Bengali language detection because
    the spoken language is Manipuri (Meiteilon), not Bengali.
    """
    def __init__(
        self,
        model_size: str = "large-v3-turbo",
        device: str = "cpu",
        compute_type: str = "int8",
    ):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def load_model(self) -> None:
        """Load the model only when this experimental pipeline is used."""
        if self.model is not None:
            return
        logger.info(
            "Loading experimental STT model: %s",
            self.model_size,
        )
        self.model = WhisperModel(
            self.model_size,
            device=self.device,
            compute_type=self.compute_type,
        )
        logger.info("Experimental STT model loaded.")

    def transcribe(self, audio_path: str) -> dict[str, Any]:
        """
        Transcribe an audio file and return the raw transcription.
        Note:
        Whisper's ability to produce accurate Manipuri text in Bengali
        script must be evaluated using actual audio samples.
        """
        path = Path(audio_path)
        if not path.exists():
            return {
                "success": False,
                "error": f"Audio file not found: {audio_path}",
            }
        try:
            self.load_model()
            segments, info = self.model.transcribe(
                str(path),
                language="bn",
                beam_size=5,
                vad_filter=True,
            )

            segment_list = list(segments)
            transcription = " ".join(
                segment.text.strip()
                for segment in segment_list
                if segment.text.strip()
            ).strip()
            return {
                "success": True,
                "text": transcription,
                "detected_language": info.language,
                "language_probability": info.language_probability,
                "script": "bengali",
                "model": self.model_size,
            }
        except Exception as exc:
            logger.exception("Experimental Bengali-script STT failed.")
            return {
                "success": False,
                "error": str(exc),
            }