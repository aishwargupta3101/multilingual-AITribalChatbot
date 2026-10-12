
import io
import threading
import logging

import numpy as np
import soundfile as sf
import torch

from scipy.signal import resample_poly
from transformers import AutoProcessor, Wav2Vec2ForCTC
logger = logging.getLogger(__name__)

class MMSASRService:
    MODEL_NAME = "facebook/mms-1b-all"
    LANGUAGE_CODE = "mni"
    SAMPLE_RATE = 16000
    def __init__(self):
        self.processor = None
        self.model = None
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )
        self.lock = threading.Lock()
        logger.info("MMS ASR device: %s", self.device)

    def load_model(self):
        if self.model is not None:
            return
        with self.lock:
            if self.model is not None:
                return
            logger.info("Loading MMS ASR model: %s", self.MODEL_NAME)
            self.processor = AutoProcessor.from_pretrained(
                self.MODEL_NAME
            )
            self.model = Wav2Vec2ForCTC.from_pretrained(
                self.MODEL_NAME
            )
            self.processor.tokenizer.set_target_lang(
                self.LANGUAGE_CODE
            )
            self.model.load_adapter(self.LANGUAGE_CODE)
            self.model.to(self.device)
            self.model.eval()
            logger.info("MMS ASR model loaded successfully.")

    def _prepare_audio(self, audio_bytes: bytes):
        audio, sample_rate = sf.read(
            io.BytesIO(audio_bytes),
            dtype="float32"
        )
        if audio.size == 0:
            raise ValueError("The uploaded audio is empty.")
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        # Resample to 16 kHz when required.
        if sample_rate != self.SAMPLE_RATE:
            from math import gcd
            divisor = gcd(sample_rate, self.SAMPLE_RATE)
            audio = resample_poly(
                audio,
                self.SAMPLE_RATE // divisor,
                sample_rate // divisor
            ).astype(np.float32)
        return audio
    def transcribe(self, audio_bytes: bytes) -> str:
        self.load_model()
        audio = self._prepare_audio(audio_bytes)
        inputs = self.processor(
            audio,
            sampling_rate=self.SAMPLE_RATE,
            return_tensors="pt"
        )
        inputs = {
            key: value.to(self.device)
            for key, value in inputs.items()
        }
        with torch.inference_mode():
            logits = self.model(**inputs).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = self.processor.batch_decode(
            predicted_ids
        )[0]
        transcription = transcription.strip()
        logger.info(
            "MMS transcription completed. Characters: %s",
            len(transcription)
        )
        return transcription
mms_asr_service = MMSASRService()