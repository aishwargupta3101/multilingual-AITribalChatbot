from pydantic import BaseModel,Field
from typing import Optional
from datetime import datetime

class ChatRequest(BaseModel):
    session_id:str = Field(...,description="User Session ID")
    question:str= Field(...,min_length=1)
    language: str=Field(...,description="User language")

class ChatResponse(BaseModel):
    success:bool
    answer:str
    language:str
    timestamp:datetime