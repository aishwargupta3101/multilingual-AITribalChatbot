
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from backend.experimental_voice.bengali_script.gpu_tts import ExperimentalGPUTTS

router = APIRouter(prefix="/experimental/voice", tags=["Experimental Voice"])

class ManipuriTTSRequest(BaseModel):
    text: str
    script: str = "bengali"

@router.post("/tts")
def generate_manipuri_tts(request: ManipuriTTSRequest):
    try:
        if request.script not in ["bengali", "meitei_mayek"]:
            raise HTTPException(status_code=400, detail="Script must be bengali or meitei_mayek")
        filename = f"manipuri_{request.script}_{uuid4().hex}.wav"
        tts = ExperimentalGPUTTS()
        result = tts.generate(text=request.text, script=request.script, output_name=filename)
        audio_path = Path(result["audio_path"])
        if not audio_path.exists():
            raise HTTPException(status_code=500, detail="Generated audio file not found")
        return FileResponse(path=audio_path, media_type="audio/wav", filename=filename)
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))