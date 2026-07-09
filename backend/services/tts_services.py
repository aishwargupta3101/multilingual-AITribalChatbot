from backend.schemas.tts import(
    TTSRequest,
    TTSResponse
)
class TTSService:
    @staticmethod
    async def generate_audio(requets: TTSRequest):
        return TTSResponse(
            success=True,
            audio_path="audio/output.wav"
        )