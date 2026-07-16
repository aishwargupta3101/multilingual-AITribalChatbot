from fastapi import APIRouter
from backend.routes.health import router as health_router
from backend.routes.chat import router as chat_router
from backend.routes.translation import router as translation_router
from backend.routes.tts import router as tts_router
from backend.routes.speech import router as speech_router
from backend.routes.history import router as history_router
from backend.routes.session import router as session_router
from backend.routes.llama_test import router as llama_test_router
from backend.routes.stream import router as stream_router
from backend.routes.upload import router as upload_router
from backend.routes.document_test import router as document_test_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router)
api_router.include_router(chat_router)
api_router.include_router(speech_router)
api_router.include_router(translation_router)
api_router.include_router(tts_router)
api_router.include_router(
    upload_router,
    tags=["Upload"]
)
api_router.include_router(
    speech_router,
    prefix="/speech",
    tags=["Speech"]

)
api_router.include_router(
    history_router,
    tags=["History"]
)
api_router.include_router(
    session_router,
    tags=["Sessions"]
)
api_router.include_router(
    llama_test_router,
    tags=["Llama Test"]
)
api_router.include_router(
    stream_router,
    tags=["Streaming"]
)
api_router.include_router(
    document_test_router,
    tags=["Document Test"]
)