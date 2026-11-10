"""Non-commercial research-only Gondi (Adilabad) MMS candidate adapters.

Both MMS candidate model cards are CC-BY-NC-4.0. These factories fail closed
unless the caller explicitly acknowledges non-commercial research use. Do not
put these models into a commercial/public service without independent written
licensing permission. This module is never automatically imported by the API.
"""
from __future__ import annotations

import io
import os
import threading
from typing import Any


class GondiMMSLicenseGateError(RuntimeError):
    pass


def _require_noncommercial(acknowledged: bool, commercial_deployment: bool, written_permission: bool) -> None:
    if commercial_deployment and not written_permission:
        raise GondiMMSLicenseGateError(
            "The selected MMS Gondi candidate is CC-BY-NC-4.0. Do not use it in a commercial product/service without written licensing permission."
        )
    if not acknowledged:
        raise GondiMMSLicenseGateError(
            "Set noncommercial_acknowledged=True only for a deliberate non-commercial research/demo evaluation."
        )


def make_gondi_adilabad_mms_stt_service(*, noncommercial_acknowledged: bool = False,
                                          commercial_deployment: bool = False,
                                          written_permission: bool = False):
    """Return the Step 2 MMS STT service for Gondi Adilabad (`wsg`) only."""
    _require_noncommercial(noncommercial_acknowledged, commercial_deployment, written_permission)
    try:
        from .stt_service import TribalMMSSTTService
    except ImportError as exc:
        raise RuntimeError("Copy the existing Step 2 stt_service.py before using this adapter.") from exc
    return TribalMMSSTTService(adapter_codes={"gondi_adilabad": "wsg"})


class GondiAdilabadMmsTTS:
    """Lazy `facebook/mms-tts-wsg` backend; experimental and license-gated."""
    MODEL_ID = "facebook/mms-tts-wsg"

    def __init__(self, *, noncommercial_acknowledged: bool = False,
                 commercial_deployment: bool = False, written_permission: bool = False) -> None:
        _require_noncommercial(noncommercial_acknowledged, commercial_deployment, written_permission)
        self._model: Any = None
        self._tokenizer: Any = None
        self._device: Any = None
        self._lock = threading.RLock()

    def _load(self):
        with self._lock:
            if self._model is not None:
                return
            try:
                import torch
                from transformers import AutoTokenizer, VitsModel
            except ImportError as exc:
                raise RuntimeError("Install torch and transformers before evaluating Gondi MMS TTS.") from exc
            device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            token = os.getenv("HF_TOKEN", "").strip()
            token_args = {"token": token} if token else {}
            self._tokenizer = AutoTokenizer.from_pretrained(self.MODEL_ID, **token_args)
            self._model = VitsModel.from_pretrained(self.MODEL_ID, **token_args).to(device)
            self._model.eval()
            self._device = device

    def __call__(self, text: str, language: str = "gondi_adilabad") -> bytes:
        if str(language).strip().lower() not in {"gondi_adilabad", "wsg"}:
            raise ValueError("This checkpoint is for Gondi, Adilabad (wsg), not all Gondi varieties.")
        text = str(text).strip()
        if not text:
            raise ValueError("Text must not be empty.")
        self._load()
        import soundfile as sf
        import torch
        inputs = self._tokenizer(text, return_tensors="pt").to(self._device)
        with torch.inference_mode():
            waveform = self._model(**inputs).waveform
        audio = waveform.squeeze().detach().cpu().numpy()
        if getattr(audio, "size", 0) == 0:
            raise RuntimeError("MMS Gondi TTS returned empty audio.")
        buffer = io.BytesIO()
        sf.write(buffer, audio, int(self._model.config.sampling_rate), format="WAV", subtype="PCM_16")
        return buffer.getvalue()
