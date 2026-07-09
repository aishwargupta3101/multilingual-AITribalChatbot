from backend.schemas.translation import (
    TranslationRequest,
    TranslationResponse
)
class TranslationService:
    @staticmethod
    async  def translate(request:TranslationRequest):
        return TranslationResponse(
            success=True,
            translated_text=request.text
        )