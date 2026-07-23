from fastapi import APIRouter,HTTPException
from backend.schemas.translation import (
    TranslationResponse,
    TranslationRequest
)
from backend.services.translation_service import translation_service

router = APIRouter(
    prefix="/translation",
    tags=["Translation"]
)

@router.post(
    "",
    response_model=TranslationResponse
)
async def translate(request:TranslationRequest):
    try:
        translated_text = translation_service.translate(
            text=request.text,
            source_language=request.source_language,
            target_language=request.target_language
        )
        return TranslationResponse(
            success=True,
            translated_text=translated_text

        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
