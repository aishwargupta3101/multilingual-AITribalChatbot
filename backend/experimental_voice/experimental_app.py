
from fastapi import FastAPI
from backend.experimental_voice.api import router

app = FastAPI(title="Experimental Manipuri TTS API")
app.include_router(router)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "experimental-manipuri-tts"}