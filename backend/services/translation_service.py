from backend.schemas.translation import TranslationRequest
from backend.utils.response import ResponseBuilder
class TranslationService:
    async  def translate(
            self,
            request:TranslationRequest
    ):
        return ResponseBuilder.success(
            message="Translation ccompleted",
            data={
                "translated_text":request.text,
                "target_language":request.target_language
            }

        )