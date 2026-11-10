"""Opt-in API routes for experimental Santali inference.

Routes are safe-off by default. Heavy model classes are imported and instantiated
only when an explicitly enabled endpoint is called. This router is separate from
existing chat/translation/Manipuri routes.
"""
from __future__ import annotations

import logging
import os
import threading
from typing import Any

from dotenv import load_dotenv
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field
from starlette.responses import Response

from .model_candidates import resolve_indictrans2_route

logger = logging.getLogger(__name__)
# Make project .env keys available to lazy model loaders, without overwriting
# variables already injected by the hosting platform.
load_dotenv(override=False)

router = APIRouter(
    prefix="/api/v1/tribal-languages/santali",
    tags=["Santali Experimental"],
)

_MAX_AUDIO_BYTES = 25 * 1024 * 1024
_backend_lock = threading.RLock()
_backends: dict[str, Any] = {}


def _flag(name: str) -> bool:
    return os.getenv(name, "").strip().lower() in {"1", "true", "yes", "on"}


def _normalise_language(language: str) -> str:
    aliases = {
        "en": "english", "eng": "english", "eng_latn": "english",
        "hi": "hindi", "hin": "hindi", "hin_deva": "hindi",
        "sat": "santali", "sat_olck": "santali",
    }
    value = str(language or "").strip().lower().replace("-", "_").replace(" ", "_")
    return aliases.get(value, value)


def _feature_flags(capability: str) -> dict[str, bool]:
    prefix = f"TRIBAL_SANTALI_{capability.upper()}"
    enabled = _flag(f"{prefix}_ENABLED")
    access_accepted = _flag(f"{prefix}_HF_ACCESS_ACCEPTED")
    backend = _backends.get(capability.lower())
    if capability.lower() == "translation":
        model_loaded = bool(getattr(backend, "_cache", {})) if backend is not None else False
    else:
        model_loaded = bool(getattr(backend, "_model", None)) if backend is not None else False
    return {
        "enabled": enabled,
        "hf_access_accepted": access_accepted,
        "ready_to_attempt_inference": enabled and access_accepted,
        "adapter_initialized": backend is not None,
        "model_loaded": model_loaded,
    }


def _require_capability(capability: str) -> None:
    prefix = f"TRIBAL_SANTALI_{capability.upper()}"
    if not _flag(f"{prefix}_ENABLED"):
        raise HTTPException(
            status_code=503,
            detail=f"Santali {capability.lower()} is disabled. Set {prefix}_ENABLED=true only after review.",
        )
    if not _flag(f"{prefix}_HF_ACCESS_ACCEPTED"):
        raise HTTPException(
            status_code=503,
            detail=(
                f"Hugging Face access conditions for the selected Santali {capability.lower()} model "
                f"must be accepted first. Set {prefix}_HF_ACCESS_ACCEPTED=true only after accepting them."
            ),
        )


def _get_backend(capability: str) -> Any:
    """Instantiate a selected adapter once; never load weights during import."""
    with _backend_lock:
        if capability in _backends:
            return _backends[capability]
        # Imports of heavyweight model wrappers are deferred until first request.
        from .experimental_santali_backends import (
            SantaliIndicConformerSTT,
            SantaliIndicTrans2Translator,
            SantaliParlerTTS,
        )

        hf_accepted = True  # caller has passed _require_capability's explicit gate
        if capability == "stt":
            backend = SantaliIndicConformerSTT(hf_access_accepted=hf_accepted)
        elif capability == "translation":
            backend = SantaliIndicTrans2Translator(hf_access_accepted=hf_accepted)
        elif capability == "tts":
            backend = SantaliParlerTTS(hf_access_accepted=hf_accepted)
        else:
            raise ValueError(f"Unknown Santali capability: {capability}")
        _backends[capability] = backend
        return backend


class SantaliTranslationRequest(BaseModel):
    text: str = Field(min_length=1, max_length=10_000)
    source_language: str = Field(min_length=1, max_length=32)
    target_language: str = Field(min_length=1, max_length=32)


@router.get("/status")
def santali_status() -> dict[str, Any]:
    """Report configuration state without claiming model/runtime availability."""
    return {
        "language": "santali",
        "status": "experimental",
        "script_target": "Ol Chiki for IndicTrans2; verify actual speech/TTS script quality",
        "capabilities": {
            "stt": _feature_flags("stt"),
            "translation": _feature_flags("translation"),
            "tts": _feature_flags("tts"),
        },
        "translation_verified_pairs": sorted(
            pair.strip().lower()
            for pair in os.getenv("TRIBAL_SANTALI_TRANSLATION_VERIFIED_PAIRS", "").split(",")
            if pair.strip()
        ),
        "note": (
            "Configuration only; successful model loading, output quality, and native-speaker evaluation "
            "are not established by this status response."
        ),
    }


@router.post("/stt")
async def santali_speech_to_text(audio: UploadFile = File(...)) -> dict[str, Any]:
    """Transcribe a Santali audio upload to text. Disabled by default."""
    _require_capability("stt")
    audio_bytes = await audio.read(_MAX_AUDIO_BYTES + 1)
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="The uploaded audio is empty.")
    if len(audio_bytes) > _MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio exceeds the 25 MB limit.")
    try:
        backend = _get_backend("stt")
        text = await run_in_threadpool(backend.transcribe, audio_bytes, "santali")
        if not isinstance(text, str) or not text.strip():
            raise RuntimeError("STT model returned empty text")
        return {
            "success": True,
            "language": "santali",
            "text": text.strip(),
            "model_id": "ai4bharat/indic-conformer-600m-multilingual",
            "status": "experimental_output_requires_native-speaker_review",
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Santali STT inference failed")
        raise HTTPException(
            status_code=503,
            detail=(
                "Santali STT inference failed. Check backend logs, model access/token, "
                "dependencies, memory, and model compatibility."
            ),
        ) from exc


@router.post("/translate")
def santali_translate(request: SantaliTranslationRequest) -> dict[str, Any]:
    """Translate only explicitly listed, human-reviewed pairs involving Santali."""
    _require_capability("translation")
    source = _normalise_language(request.source_language)
    target = _normalise_language(request.target_language)
    try:
        model_id, source_code, target_code = resolve_indictrans2_route(source, target)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    # No translation direction is assumed quality-verified. The owner must add
    # each direction only after evaluation of representative human-reviewed samples.
    pair_key = f"{source}->{target}"
    reviewed_pairs = {
        pair.strip().lower()
        for pair in os.getenv("TRIBAL_SANTALI_TRANSLATION_VERIFIED_PAIRS", "").split(",")
        if pair.strip()
    }
    if pair_key not in reviewed_pairs:
        raise HTTPException(
            status_code=409,
            detail=(
                f"Translation pair '{pair_key}' is not enabled. Evaluate this exact direction with "+
                "native speakers, then add it to TRIBAL_SANTALI_TRANSLATION_VERIFIED_PAIRS."
            ),
        )

    try:
        backend = _get_backend("translation")
        translated = backend(request.text, source, target)
        if not isinstance(translated, str) or not translated.strip():
            raise RuntimeError("Translation model returned empty output")
        return {
            "success": True,
            "source_language": source,
            "target_language": target,
            "source_model_token": source_code,
            "target_model_token": target_code,
            "translated_text": translated.strip(),
            "model_id": model_id,
            "status": "experimental_output_requires_native-speaker_review",
        }
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Santali translation inference failed")
        raise HTTPException(
            status_code=503,
            detail=(
                "Santali translation failed. Check backend logs, gated-model access/token, "
                "dependencies, memory, and model compatibility."
            ),
        ) from exc


@router.post("/tts")
def santali_text_to_speech(text: str = Form(..., min_length=1, max_length=10_000)) -> Response:
    """Generate a WAV from Santali text. Disabled by default."""
    _require_capability("tts")
    if not text.strip():
        raise HTTPException(status_code=400, detail="Text must not be empty.")
    if len(text) > 10_000:
        raise HTTPException(status_code=413, detail="Text exceeds the 10,000-character limit.")
    try:
        backend = _get_backend("tts")
        audio_bytes = backend(text, language="santali")
        if not isinstance(audio_bytes, bytes) or not audio_bytes:
            raise RuntimeError("TTS model returned empty audio")
        return Response(
            content=audio_bytes,
            media_type="audio/wav",
            headers={"Content-Disposition": 'attachment; filename="santali.wav"'},
        )
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Santali TTS inference failed")
        raise HTTPException(
            status_code=503,
            detail=(
                "Santali TTS inference failed. Check backend logs, gated-model access/token, "
                "dependencies, memory, and model compatibility."
            ),
        ) from exc
