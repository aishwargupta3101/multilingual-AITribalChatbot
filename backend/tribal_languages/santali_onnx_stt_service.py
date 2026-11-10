"""Lazy Santali speech recognition via the CPU ONNX export.

This module is additive and independent from the existing PyTorch Santali adapter.
It reuses OpenVoiceOS' Santali ONNX export and the onnx-asr API.
"""
from __future__ import annotations

import io
import threading
from typing import Any

MODEL_ID = "OpenVoiceOS/ai4bharat-indicconformer-sat-onnx"
LANGUAGE = "santali"
SAMPLE_RATE = 16_000
MIN_AVAILABLE_RAM_GB = 2.0
MAX_AUDIO_SECONDS = 120.0


class SantaliOnnxSTTService:
    """Lazy, process-local singleton-friendly ASR service. CPU inference only."""

    def __init__(self) -> None:
        self._model: Any = None
        self._lock = threading.RLock()

    @property
    def model_loaded(self) -> bool:
        return self._model is not None

    def _ensure_memory(self) -> None:
        try:
            import psutil
        except ImportError:
            return
        available_gb = psutil.virtual_memory().available / (1024 ** 3)
        if available_gb < MIN_AVAILABLE_RAM_GB:
            raise RuntimeError(
                f"Only {available_gb:.2f} GB RAM is available; refusing to load/use "
                f"the Santali ONNX model below {MIN_AVAILABLE_RAM_GB:.1f} GB."
            )

    def _load_model(self):
        with self._lock:
            if self._model is not None:
                return self._model
            self._ensure_memory()
            try:
                import onnx_asr
            except ImportError as exc:
                raise RuntimeError(
                    "onnx-asr is missing. Install it with: "
                    'python -m pip install "onnx-asr[cpu,hub]"'
                ) from exc

            # quantization=None selects the unquantized ONNX graph. The INT8
            # graph raised ConvInteger(10) NOT_IMPLEMENTED on this user's CPU runtime.
            model = onnx_asr.load_model(
                MODEL_ID,
                quantization=None,
                providers=["CPUExecutionProvider"],
            )
            self._model = model
            return model

    @staticmethod
    def _decode_audio(audio_bytes: bytes):
        try:
            import av
            import numpy as np
        except ImportError as exc:
            raise RuntimeError(
                "Audio decoding requires PyAV and NumPy. Install av and numpy."
            ) from exc

        try:
            container = av.open(io.BytesIO(audio_bytes))
        except Exception as exc:
            raise ValueError(
                "Could not open the uploaded audio. Provide a valid audio file."
            ) from exc

        chunks = []
        try:
            stream = next((s for s in container.streams if s.type == "audio"), None)
            if stream is None:
                raise ValueError("The uploaded file contains no audio stream.")
            resampler = av.AudioResampler(
                format="fltp", layout="mono", rate=SAMPLE_RATE
            )
            for frame in container.decode(audio=stream.index):
                converted_frames = resampler.resample(frame) or []
                for converted in converted_frames:
                    chunks.append(
                        converted.to_ndarray().reshape(-1).astype(np.float32)
                    )
            for converted in (resampler.resample(None) or []):
                chunks.append(
                    converted.to_ndarray().reshape(-1).astype(np.float32)
                )
        except ValueError:
            raise
        except Exception as exc:
            raise ValueError("Could not decode or resample the uploaded audio.") from exc
        finally:
            container.close()

        if not chunks:
            raise ValueError("The uploaded audio contains no decodable samples.")
        waveform = np.concatenate(chunks).astype(np.float32, copy=False)
        duration = len(waveform) / SAMPLE_RATE
        if duration <= 0:
            raise ValueError("The uploaded audio has no duration.")
        if duration > MAX_AUDIO_SECONDS:
            raise ValueError(
                f"Audio is {duration:.1f} seconds long; the limit is "
                f"{MAX_AUDIO_SECONDS:.0f} seconds."
            )
        return waveform, duration

    def transcribe_bytes(self, audio_bytes: bytes) -> dict[str, Any]:
        if not audio_bytes:
            raise ValueError("The uploaded audio is empty.")
        waveform, duration = self._decode_audio(audio_bytes)
        self._ensure_memory()
        model = self._load_model()
        try:
            prediction = model.recognize(waveform, sample_rate=SAMPLE_RATE)
        except Exception as exc:
            raise RuntimeError(
                "Santali ONNX inference failed. Check the backend logs and model/runtime compatibility."
            ) from exc

        if isinstance(prediction, (list, tuple)):
            prediction = prediction[0] if prediction else ""
        text = str(prediction).strip()
        if not text:
            raise RuntimeError("The Santali ONNX model returned an empty transcription.")

        return {
            "success": True,
            "language": LANGUAGE,
            "text": text,
            "model_id": MODEL_ID,
            "duration_seconds": round(duration, 2),
            "status": "experimental_output_requires_broader_evaluation",
        }
