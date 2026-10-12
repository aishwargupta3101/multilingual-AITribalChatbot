
import os
import tempfile
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.speech.speech_service import speech_service
from backend.services.translation_service import translation_service

router = APIRouter(
    prefix="/api/v1/speech",
    tags=["Speech"]
)

SUPPORTED_LANGUAGES = {
    "english",
    "hindi",
    "manipuri",
}


def normalize_language(language: str) -> str:
    """Normalize and validate a language identifier."""
    normalized = language.strip().lower()

    if normalized not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported language: {language}. "
                f"Supported languages: {', '.join(sorted(SUPPORTED_LANGUAGES))}"
            )
        )

    return normalized


async def save_temp_audio(audio: UploadFile) -> str:
    """Save uploaded audio to a temporary file."""
    suffix = Path(audio.filename or "audio.wav").suffix or ".wav"

    audio_bytes = await audio.read()

    if not audio_bytes:
        raise HTTPException(
            status_code=400,
            detail="Audio file is empty."
        )

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=suffix
        ) as temp:
            temp.write(audio_bytes)
            temp_path = temp.name

        return temp_path

    except OSError as exc:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)

        raise HTTPException(
            status_code=500,
            detail="Unable to save uploaded audio."
        ) from exc


def cleanup_temp_audio(temp_path: str) -> None:
    """Remove temporary audio files safely."""
    try:
        if os.path.exists(temp_path):
            os.remove(temp_path)
    except OSError:
        pass


@router.post("/upload")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: str = Form("english")
):
    """Convert uploaded speech into text."""
    language = normalize_language(language)
    temp_path = await save_temp_audio(audio)

    try:
        result = await speech_service.speech_to_text(
            audio_path=temp_path,
            language=language
        )

        return result

    finally:
        cleanup_temp_audio(temp_path)


@router.post("/translate")
async def speech_translate(
    audio: UploadFile = File(...),
    input_language: str = Form("english"),
    response_language: str = Form("hindi")
):
    """
    Transcribe speech and translate it into the selected language.

    This endpoint performs translation only.
    It does not invoke Llama 3.
    """
    input_language = normalize_language(input_language)
    response_language = normalize_language(response_language)

    temp_path = await save_temp_audio(audio)

    try:
        transcription = await speech_service.speech_to_text(
            audio_path=temp_path,
            language=input_language
        )

        if not isinstance(transcription, dict):
            raise HTTPException(
                status_code=500,
                detail="Invalid response from speech recognition service."
            )

        if not transcription.get("success"):
            return {
                "success": False,
                "error": transcription.get(
                    "error",
                    "Speech recognition failed."
                ),
                "transcription": "",
                "translated_text": ""
            }

        original_text = str(
            transcription.get("text") or ""
        ).strip()

        if not original_text:
            return {
                "success": False,
                "error": "No speech could be recognized.",
                "transcription": "",
                "translated_text": ""
            }

        if input_language == response_language:
            translated_text = original_text

        else:
            translated_text = translation_service.translate(
                text=original_text,
                source_language=input_language,
                target_language=response_language
            )
        translated_text = str(translated_text or "").strip()
        if not translated_text:
            return {
                "success": False,
                "error": "Translation returned empty text.",
                "transcription": original_text,
                "translated_text": ""
            }

        return {
            "success": True,
            "transcription": original_text,
            "translated_text": translated_text,
            "input_language": input_language,
            "response_language": response_language,
            "detected_language": transcription.get("language"),
            "confidence": transcription.get("confidence", 0)
        }
    finally:
        cleanup_temp_audio(temp_path)