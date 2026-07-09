from pydantic import BaseModel
from typing import Optional
class SpeechRequest(BaseModel):
    language:str

class SpeechResponse(BaseModel):
    success:bool
    transcript:str
    detected_language:Optional[str]= None