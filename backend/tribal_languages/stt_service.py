"""Additive, lazy-loaded MMS ASR service for new tribal-language modules.

This service is deliberately separate from backend.services.mms_asr_service,
which is configured for Manipuri (mni). A language must have a verified MMS
adapter code explicitly supplied before inference is allowed.
"""
from __future__ import annotations

import io
import logging
import threading
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


class STTConfigurationError(ValueError):
    """Raised when the requested language/model configuration is incomplete."""


@dataclass(frozen=True)
class STTResult:
    text: str
    language: str
    model_id: str
    adapter_code: str


class TribalMMSSTTService:
    """Lazy MMS-1B adapter runner for explicitly validated language codes.

    `adapter_codes` maps internal registry keys (e.g. ``santali``) to a model
    adapter code that has already been checked against the selected checkpoint.
    No code is assumed from ISO identifiers because MMS adapter identifiers can
    differ from broad language labels or variety names.
    """

    SAMPLE_RATE = 16_000
    DEFAULT_MODEL_ID = "facebook/mms-1b-all"

    def __init__(
        self,
        adapter_codes: dict[str, str] | None = None,
        model_id: str = DEFAULT_MODEL_ID,
    ) -> None:
        self.adapter_codes = {
            key.strip().lower(): value.strip()
            for key, value in (adapter_codes or {}).items()
            if key.strip() and value.strip()
        }
        self.model_id = model_id.strip() or self.DEFAULT_MODEL_ID
        self._models: dict[tuple[str, str], tuple[Any, Any, Any]] = {}
        self._lock = threading.RLock()

    @staticmethod
    def _language_key(language: str) -> str:
        key = language.strip().lower().replace(" ", "_")
        if not key:
            raise STTConfigurationError("A language key is required.")
        return key

    def _get_adapter_code(self, language: str, adapter_code: str | None) -> str:
        key = self._language_key(language)
        code = (adapter_code or self.adapter_codes.get(key) or "").strip()
        if not code:
            raise STTConfigurationError(
                f"No verified MMS adapter code is configured for '{key}'. "
                "Verify the exact language variety and checkpoint adapter first, "
                "then pass adapter_code explicitly or configure adapter_codes."
            )
        return code

    def _load(self, adapter_code: str) -> tuple[Any, Any, Any]:
        cache_key = (self.model_id, adapter_code)
        with self._lock:
            if cache_key in self._models:
                return self._models[cache_key]

            # Import heavyweight dependencies only when inference is requested.
            try:
                import torch
                from transformers import AutoProcessor, Wav2Vec2ForCTC
            except ImportError as exc:
                raise RuntimeError(
                    "MMS STT dependencies are missing. Install the project's "
                    "existing torch and transformers dependencies."
                ) from exc

            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            logger.info(
                "Loading tribal MMS ASR model=%s adapter=%s device=%s",
                self.model_id,
                adapter_code,
                device,
            )
            try:
                processor = AutoProcessor.from_pretrained(self.model_id)
                model = Wav2Vec2ForCTC.from_pretrained(self.model_id)
                processor.tokenizer.set_target_lang(adapter_code)
                model.load_adapter(adapter_code)
                model.to(device)
                model.eval()
            except Exception as exc:
                raise RuntimeError(
                    f"Could not load MMS adapter '{adapter_code}' from "
                    f"'{self.model_id}'. Confirm that this checkpoint exposes "
                    "the adapter and that the model licence is suitable."
                ) from exc

            loaded = (processor, model, device)
            self._models[cache_key] = loaded
            return loaded

    @classmethod
    def _prepare_audio(cls, audio_bytes: bytes):
        if not audio_bytes:
            raise ValueError("The uploaded audio is empty.")
        try:
            import numpy as np
            import soundfile as sf
            from scipy.signal import resample_poly
        except ImportError as exc:
            raise RuntimeError(
                "Audio dependencies are missing. The project requires numpy, "
                "soundfile, and scipy for this STT path."
            ) from exc

        try:
            audio, sample_rate = sf.read(io.BytesIO(audio_bytes), dtype="float32")
        except Exception as exc:
            raise ValueError(
                "Could not decode audio. Supply a supported audio file, such as WAV or FLAC."
            ) from exc
        if audio.size == 0:
            raise ValueError("The uploaded audio contains no samples.")
        if audio.ndim > 1:
            audio = np.mean(audio, axis=1)
        if sample_rate <= 0:
            raise ValueError("The audio sample rate is invalid.")
        if sample_rate != cls.SAMPLE_RATE:
            from math import gcd
            divisor = gcd(int(sample_rate), cls.SAMPLE_RATE)
            audio = resample_poly(
                audio,
                cls.SAMPLE_RATE // divisor,
                int(sample_rate) // divisor,
            ).astype(np.float32)
        return audio

    def transcribe(
        self,
        language: str,
        audio_bytes: bytes,
        *,
        adapter_code: str | None = None,
    ) -> STTResult:
        """Transcribe audio only when a verified adapter code is configured."""
        key = self._language_key(language)
        code = self._get_adapter_code(key, adapter_code)
        audio = self._prepare_audio(audio_bytes)
        processor, model, device = self._load(code)

        import torch
        inputs = processor(
            audio,
            sampling_rate=self.SAMPLE_RATE,
            return_tensors="pt",
        )
        inputs = {name: value.to(device) for name, value in inputs.items()}
        with torch.inference_mode():
            logits = model(**inputs).logits
        token_ids = torch.argmax(logits, dim=-1)
        text = processor.batch_decode(token_ids)[0].strip()
        logger.info("Tribal MMS transcription completed for %s (%d chars)", key, len(text))
        return STTResult(
            text=text,
            language=key,
            model_id=self.model_id,
            adapter_code=code,
        )
tribal_mms_stt_service = TribalMMSSTTService()
