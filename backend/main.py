from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import api_router
from backend.config.logger import logger
from backend.config.settings import settings
from backend.database.connection import mongodb
from backend.database.indexes import create_indexes
from backend.middleware import(
    LoggingMiddleware,
    TimerMiddleware,
    RequestIDMiddleware
)
from backend.exceptions import(
    TribalAIException,
    tribal_exception_handler,
    generic_exception_handler,
)
from backend.api.translation import router as translation_router
from backend.speech.speech_router import router as speech_router
from backend.tts.tts_router import router as tts_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Tribal AI Chatbot Backend...")
    await mongodb.connect()
    await create_indexes()
    yield
    await mongodb.disconnect()
    logger.info("Stopping Tribal AI Chatbot Backend....")
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TimerMiddleware)
app.add_middleware(LoggingMiddleware)
app.include_router(api_router)

app.include_router(speech_router)
app.add_exception_handler(Exception, generic_exception_handler)
app.add_exception_handler(TribalAIException,tribal_exception_handler)


@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0",
    }
