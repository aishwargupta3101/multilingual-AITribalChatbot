from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from backend.services.video_learning_service import (
    video_learning_service,
    VideoLearningError,
    VideoLearningRateLimitError,
)
from backend.config.logger import logger

router = APIRouter(prefix="/video-learning", tags=["Video Learning"])


class VideoLessonRequest(BaseModel):
    url: str = Field(..., min_length=8, max_length=1000)
    level: str = Field(default="beginner")
    output_language: str = Field(default="english")


@router.post("/lesson")
async def create_video_lesson(request: VideoLessonRequest):
    try:
        result = await video_learning_service.create_lesson(
            url=request.url,
            level=request.level,
            output_language=request.output_language,
        )
        return {"success": True, "data": result}
    except VideoLearningRateLimitError as exc:
        # 429 accurately tells clients that the AI provider quota/rate limit is the blocker.
        raise HTTPException(status_code=429, detail=str(exc)) from exc
    except VideoLearningError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Unexpected video learning error")
        raise HTTPException(status_code=500, detail="Video lesson generation failed unexpectedly.") from exc
