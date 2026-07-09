from backend.schemas.speech import SpeechRequest,SpeechResponse

class SpeechService:
    @staticmethod
    async def speech_to_text(request:SpeechRequest):
        return SpeechResponse(
            success=True,
            transcript="Dummy Transcript",
            detected_language=request.language
        )