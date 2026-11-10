import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from TTS.utils.synthesizer import Synthesizer

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.translation.meitei_script_converter import convert_meitei_to_bengali

FASTPITCH_MODEL = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\best_model.pth"
FASTPITCH_CONFIG = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\config.json"
SPEAKERS_FILE = r"C:\Users\kunda\Downloads\mni\mni\fastpitch\speakers.pth"
HIFIGAN_MODEL = r"C:\Users\kunda\Downloads\mni\mni\hifigan\best_model.pth"
HIFIGAN_CONFIG = r"C:\Users\kunda\Downloads\mni\mni\hifigan\config.json"

OUTPUT_DIR = Path("experimental_outputs/manipuri_tts/indic_api")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Experimental AI4Bharat Manipuri TTS")

synthesizer = None

class TTSRequest(BaseModel):
    text: str
    script: str = "bengali"
    speaker: str = "female"

def get_synthesizer():
    global synthesizer
    if synthesizer is None:
        print("Loading AI4Bharat Manipuri TTS...")
        synthesizer = Synthesizer(
            tts_checkpoint=FASTPITCH_MODEL,
            tts_config_path=FASTPITCH_CONFIG,
            tts_speakers_file=SPEAKERS_FILE,
            vocoder_checkpoint=HIFIGAN_MODEL,
            vocoder_config=HIFIGAN_CONFIG,
            use_cuda=False
        )
        print("AI4Bharat TTS loaded.")
    return synthesizer

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "experimental-ai4bharat-manipuri-tts",
        "model": "AI4Bharat Indic-TTS",
        "language": "Manipuri",
        "device": "cpu"
    }

@app.post("/tts")
def generate_tts(request: TTSRequest):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")

    if request.script not in {"bengali", "meitei_mayek"}:
        raise HTTPException(
            status_code=400,
            detail="Script must be bengali or meitei_mayek."
        )

    if request.speaker not in {"female", "male"}:
        raise HTTPException(
            status_code=400,
            detail="Speaker must be female or male."
        )

    text = request.text.strip()

    if request.script == "meitei_mayek":
        text = convert_meitei_to_bengali(text)

    text = text.replace("।", "").strip()

    tts = get_synthesizer()

    try:
        wav = tts.tts(
            text=text,
            speaker_name=request.speaker
        )

        output_path = OUTPUT_DIR / "manipuri_api.wav"

        import numpy as np
        import wave

        audio = np.asarray(wav)

        if audio.dtype != np.int16:
            audio = np.clip(audio, -1.0, 1.0)
            audio = (audio * 32767).astype(np.int16)

        with wave.open(str(output_path), "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(tts.tts_model.ap.sample_rate)
            wf.writeframes(audio.tobytes())

        return FileResponse(
            str(output_path),
            media_type="audio/wav",
            filename="manipuri_ai4bharat.wav"
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"TTS generation failed: {error}"
        )