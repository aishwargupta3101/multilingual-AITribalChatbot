from backend.schemas.speech import SpeechRequest
from backend.utils.response import ResponseBuilder

class SpeechService:
    async def speech_to_text(
            self,
            request:SpeechRequest
    ):
        return ResponseBuilder.success(
            message="Speech converted successfully",
            data={
                "transcript":"Dummy Transcript",
                "detected_language": request.language

            }
        )