from pydantic import BaseModel

class UploadResponse(BaseModel):
    filename:str
    file_type:str
    size:int
    status:str