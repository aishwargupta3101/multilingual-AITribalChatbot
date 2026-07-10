from pydantic import BaseModel
class ComponentStatus(BaseModel):
    status: str
    message: str

class HealthResponse(BaseModel):
    application: str
    version: str
    backend: ComponentStatus
    mongodb: ComponentStatus
    vector_db: ComponentStatus
    llama: ComponentStatus
    nemo: ComponentStatus
    translation: ComponentStatus