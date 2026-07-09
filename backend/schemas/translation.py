from pydantic import BaseModel
class TranslationRequest(BaseModel):
    text:str
    source_language:str
    target_language:str

class TranslationResponse(BaseModel):
    success:bool
    translated_text:str