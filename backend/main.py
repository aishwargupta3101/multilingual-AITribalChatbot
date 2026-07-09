from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import api_router
from backend.config.logger import logger
from backend.config.settings import settings
from backend.utils.exceptions import global_exception_handler

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Tribal AI Chatbot Backend...")
    yield
    logger.info("Stopping Tribal AI Chatbot Backend...")
app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8501",
        "http://127.0.0.1:8501",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)
app.add_exception_handler(Exception, global_exception_handler)

@app.get("/")
async def root():
    return {
        "app": settings.APP_NAME,
        "status": "running",
        "version": "1.0.0",
    }