"""
Faster-Whisper Speech-to-Text Service
"""

import logging
from faster_whisper import WhisperModel
logger = logging.getLogger(__name__)

class WhisperService:
    def __init__(self):
        self.model = None

    def load_model(self):
        if self.model is None:
            logger.info("=" * 60)
            logger.info("Loading Faster-Whisper Model...")
            logger.info("=" * 60)
            self.model = WhisperModel(
                model_size_or_path="medium",
                device="cpu",
                compute_type="int8"
            )
            logger.info(
                "Whisper Model Loaded Successfully"
            )

    def transcribe(
        self,
        audio_path: str,
        language: str = None
    ):

        self.load_model()
        logger.info("=" * 60)
        logger.info("🎤 USING FASTER WHISPER")
        logger.info(f"Audio File: {audio_path}")
        logger.info(f"Requested Language: {language}")
        logger.info("=" * 60)
        segments, info = self.model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True,
            language=language
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()

        logger.info(
            f"Detected Language: {info.language}"
        )
        logger.info(
            f"Language Probability: "
            f"{info.language_probability}"
        )
        logger.info(
            f"Transcribed Text: {text}"
        )
        logger.info("=" * 60)

        return {
            "text": text,
            "language": info.language,
            "language_probability": info.language_probability
        }
whisper_service = WhisperService()