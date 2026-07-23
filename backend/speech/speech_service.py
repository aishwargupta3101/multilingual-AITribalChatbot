from .whisper_service import whisper_service

class SpeechService:
    async def speech_to_text(self, audio_path: str):
        result = whisper_service.transcribe(audio_path)
        return {
            "success": True,
            "text": result["text"],
            "language": result["language"],
            "confidence": result["language_probability"]
        }
speech_service = SpeechService()