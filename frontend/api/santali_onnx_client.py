"""Isolated client for the opt-in Santali ONNX STT route.

This module does not alter the existing APIClient or existing speech endpoints.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import requests
from api.endpoints import BASE_URL

logger = logging.getLogger(__name__)
SANTALI_ONNX_STT_ENDPOINT = "/api/v1/tribal-languages/santali-onnx/stt"


class SantaliOnnxClient:
    """Small opt-in client for experimental Santali-only transcription."""

    @staticmethod
    def transcribe_file(audio_path: str | Path) -> dict[str, Any]:
        path = Path(audio_path)
        if not path.is_file():
            return {"success": False, "error": f"Audio file not found: {path}"}

        try:
            with path.open("rb") as audio_file:
                response = requests.post(
                    f"{BASE_URL}{SANTALI_ONNX_STT_ENDPOINT}",
                    files={
                        "audio": (
                            path.name,
                            audio_file,
                            "audio/wav" if path.suffix.lower() == ".wav" else "application/octet-stream",
                        )
                    },
                    timeout=(10, 300),
                )

            try:
                payload = response.json()
            except ValueError:
                payload = None

            if not response.ok:
                detail = None
                if isinstance(payload, dict):
                    detail = payload.get("detail") or payload.get("error")
                detail = detail or response.text[:1000] or "No response details provided."
                message = f"Santali ONNX STT returned HTTP {response.status_code}: {detail}"
                logger.warning(message)
                return {"success": False, "error": message, "status_code": response.status_code}

            if not isinstance(payload, dict):
                return {
                    "success": False,
                    "error": "Santali ONNX STT returned an invalid JSON response.",
                }

            if payload.get("success") is not True:
                return {
                    "success": False,
                    "error": payload.get("error") or payload.get("detail") or "Santali transcription failed.",
                }

            return payload

        except (requests.RequestException, OSError) as exc:
            logger.exception("Santali ONNX audio upload failed.")
            return {"success": False, "error": f"Could not reach Santali ONNX STT: {exc}"}
    @staticmethod
    def transcribe_bytes(audio_bytes: bytes, filename: str) -> dict[str, Any]:
        """Transcribe uploaded audio bytes without writing a temporary file."""
        if not audio_bytes:
            return {"success": False, "error": "The uploaded audio is empty."}

        safe_name = Path(filename or "santali_audio.mp3").name
        try:
            import mimetypes
            content_type = mimetypes.guess_type(safe_name)[0] or "application/octet-stream"
            response = requests.post(
                f"{BASE_URL}{SANTALI_ONNX_STT_ENDPOINT}",
                files={"audio": (safe_name, audio_bytes, content_type)},
                timeout=(10, 300),
            )
            try:
                payload = response.json()
            except ValueError:
                payload = None

            if not response.ok:
                detail = None
                if isinstance(payload, dict):
                    detail = payload.get("detail") or payload.get("error")
                detail = detail or response.text[:1000] or "No response details provided."
                message = f"Santali ONNX STT returned HTTP {response.status_code}: {detail}"
                logger.warning(message)
                return {"success": False, "error": message, "status_code": response.status_code}

            if not isinstance(payload, dict):
                return {"success": False, "error": "Santali ONNX STT returned invalid JSON."}
            if payload.get("success") is not True:
                return {
                    "success": False,
                    "error": payload.get("error") or payload.get("detail") or "Santali transcription failed.",
                }
            return payload
        except requests.RequestException as exc:
            logger.exception("Santali ONNX audio upload failed.")
            return {"success": False, "error": f"Could not reach Santali ONNX STT: {exc}"}

