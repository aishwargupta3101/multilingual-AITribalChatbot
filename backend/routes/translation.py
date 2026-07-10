from fastapi import APIRouter, Depends
from backend.api.dependencies import get_translation_service
from backend.schemas.translation import TranslationRequest
from backend.services.translation_service import TranslationService

router = APIRouter(
    prefix="/translation",
    tags=["Translation"]
)
@router.post("/")
async def translate(
    request: TranslationRequest,
    translation_service: TranslationService = Depends(get_translation_service)
):
    return await translation_service.translate(request)