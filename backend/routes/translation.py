from fastapi import APIRouter
from backend.schemas.translation import (
    TranslationRequest,TranslationResponse
)
from backend.services.translation_services import TranslationService
router = APIRouter(
    prefix="/translation",
    tags=["Translation"]
)
@router.post(
    "/",
    response_model=TranslationResponse)
async def translate(request:TranslationResponse):
    return await TranslationService.translate(request)



