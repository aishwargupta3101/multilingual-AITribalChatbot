from pydantic import BaseModel
from typing import Optional

class TTSRequest(BaseModel):
    text: str
    language: str = "english"

class TTSResponse(BaseModel):
    success: bool
    audio_file: Optional[str] = None
    error: Optional[str] = None