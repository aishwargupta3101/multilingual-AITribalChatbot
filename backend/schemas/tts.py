from pydantic import BaseModel
class TTSRequest(BaseModel):
    text:str
    language:str

class TTSResponse(BaseModel):
    success:bool
    audio_path:str