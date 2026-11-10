
from io import BytesIO
import logging
import traceback
logger = logging.getLogger(__name__)
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from backend.services.presentation_generator import PresentationGenerator

router = APIRouter(
    prefix="/api/v1/presentations",
    tags=["Presentations"],
)
class PresentationRequest(BaseModel):
    topic: str = Field(min_length=3, max_length=500)
    slide_count: int = Field(default=8, ge=3, le=15)
    source_text: str = Field(default="", max_length=12000)

@router.post("/generate")
async def generate_presentation(request: PresentationRequest):
    try:
        generator = PresentationGenerator()
        slides = await generator.generate_slides(
            topic=request.topic,
            slide_count=request.slide_count,
            source_text=request.source_text,
        )
        pptx_file = generator.create_pptx(slides)
        return StreamingResponse(
            pptx_file,
            media_type=(
                "application/vnd.openxmlformats-officedocument."
                "presentationml.presentation"
            ),
            headers={
                "Content-Disposition":
                    'attachment; filename="presentation.pptx"'
            },
        )
    except Exception as exc:
        logger.exception("Presentation generation failed")
        raise HTTPException(
            status_code=500,
            detail=f"Presentation generation failed: {type(exc).__name__}: {exc}",
        ) from exc
