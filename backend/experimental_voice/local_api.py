from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.experimental_voice.bengali_script.tts import ExperimentalManipuriTTS
app = FastAPI(title="Local Manipuri TTS")
tts = ExperimentalManipuriTTS()
class ManipuriTTSRequest(BaseModel):
    text: str
    script: str
@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "local-manipuri-tts",
        "device": tts.device
    }
@app.post("/tts")
def generate_tts(request: ManipuriTTSRequest):
    if request.script not in {"bengali", "meitei_mayek"}:
        raise HTTPException(
            status_code=400,
            detail="Script must be bengali or meitei_mayek."
        )
    result = tts.generate(
        text=request.text,
        script=request.script,
        output_name="manipuri_local.wav"
    )
    if not result.get("success"):
        raise HTTPException(
            status_code=500,
            detail=result.get("error", "TTS generation failed.")
        )
    return FileResponse(
        result["audio_path"],
        media_type="audio/wav",
        filename="manipuri_local.wav"
    )