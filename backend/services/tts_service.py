from backend.schemas.tts import TTSRequest
from backend.utils.response import ResponseBuilder
class TTSService:
    async def generate_audio(
            self,
            request: TTSRequest):
        return ResponseBuilder.success(
            message="audio generated",
            data={
                "audio_path":"audio/output"
            }
        )