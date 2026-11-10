
import os
import tempfile
import uuid
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.speech.speech_service import speech_service
from backend.speech.voice_language_capabilities import stt_languages
from backend.services.translation_service import translation_service
from backend.schemas.chat import ChatRequest
from backend.services.chat_service import chat_service

router = APIRouter(
    prefix="/api/v1/speech",
    tags=["Speech"]
)
SUPPORTED_RESPONSE_LANGUAGES = {
    "english", "hindi", "manipuri", "assamese", "bengali",
    "gujarati", "kannada", "malayalam", "marathi", "nepali",
    "punjabi", "sanskrit", "tamil", "telugu", "urdu",
}

def normalize_stt_language(language: str) -> str:
    """Normalize and validate a language used for speech recognition."""
    normalized = (language or "").strip().lower()
    available = stt_languages()

    if normalized not in available:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported input speech language: {language}. "
                f"Supported input languages: {', '.join(sorted(available))}"
            )
        )

    return normalized


def normalize_response_language(language: str) -> str:
    """Validate chatbot output language independently of STT support."""
    normalized = (language or "").strip().lower()
    if normalized not in SUPPORTED_RESPONSE_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported response language: {language}. "
                f"Supported response languages: {', '.join(sorted(SUPPORTED_RESPONSE_LANGUAGES))}"
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
    language = normalize_stt_language(language)
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
    Transcribe a spoken question, ask the existing chatbot to answer it,
    and return the answer in the selected response language.

    `translated_text` is retained for frontend compatibility and now contains
    the chatbot's answer, not merely a translation of the spoken question.
    """
    input_language = normalize_stt_language(input_language)
    response_language = normalize_response_language(response_language)

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
        if input_language == "english":
            question_for_chat = original_text
        else:
            question_for_chat = translation_service.translate(
                text=original_text,
                source_language=input_language,
                target_language="english"
            )
        question_for_chat = str(question_for_chat or "").strip()
        if not question_for_chat:
            return {
                "success": False,
                "error": "Could not prepare the recognized question for the chatbot.",
                "transcription": original_text,
                "translated_text": "",
                "answer": ""
            }

        chat_request = ChatRequest(
            session_id=f"voice-{uuid.uuid4()}",
            question=question_for_chat,
            language=response_language,
            document_id=None
        )
        chat_result = await chat_service.process_chat(chat_request)

        if not isinstance(chat_result, dict):
            raise HTTPException(
                status_code=500,
                detail="The chatbot returned an invalid response."
            )
        chat_data = chat_result.get("data")
        if not isinstance(chat_data, dict):
            chat_data = chat_result

        answer = str(
            chat_data.get("answer")
            or chat_data.get("response")
            or ""
        ).strip()

        if chat_result.get("success") is False or not answer:
            error_message = (
                chat_result.get("error")
                or chat_data.get("error")
                or "The chatbot could not generate an answer."
            )
            return {
                "success": False,
                "error": str(error_message),
                "transcription": original_text,
                "translated_text": "",
                "answer": ""
            }

        return {
            "success": True,
            "transcription": original_text,
            "translated_text": answer,
            "answer": answer,
            "input_language": input_language,
            "response_language": response_language,
            "detected_language": transcription.get("language"),
            "confidence": transcription.get("confidence", 0),
            "response_type": "chatbot_answer"
        }
    finally:
        cleanup_temp_audio(temp_path)