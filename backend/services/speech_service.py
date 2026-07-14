from pathlib import Path
from fastapi import UploadFile

class SpeechService:
    AUDIO_DIR = Path("data/audio")
    def __init__(self):
        self.AUDIO_DIR.mkdir(parents=True, exist_ok=True)

    async  def save_audio(self ,file:UploadFile):
        file_path =self.AUDIO_DIR/file.filename

        with open(file_path,"wb") as buffer:
            buffer.write(await file.read())

        return{
            "filename": file.filename,
            "path":str(file_path),
            "status":"saved"
        }