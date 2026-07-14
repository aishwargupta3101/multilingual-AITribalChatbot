from fastapi import APIRouter
from backend.routes.health import router as health_router
from backend.routes.chat import router as chat_router
from backend.routes.speech import router as speech_router
from backend.routes.translation import router as translation_router
from backend.routes.tts import router as tts_router
from backend.routes.upload import router as upload_router
from backend.routes.speech import router as speech_router


api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(chat_router)
api_router.include_router(speech_router)
api_router.include_router(translation_router)
api_router.include_router(tts_router)
api_router.include_router(
    upload_router,
    prefix="/upload",
    tags=["Upload"]
)
api_router.include_router(
    speech_router,
    prefix="/speech",
    tags=["Speech"]

)