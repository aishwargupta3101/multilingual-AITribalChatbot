from fastapi import APIRouter,File,Form,UploadFile
from backend.services.upload_service import upload_service
router = APIRouter()

@router.post("/upload")
async def upload_document(
    session_id:str =Form(...),
    file:UploadFile = File(...),

):
    return await upload_service.upload_document(
        session_id=session_id,
        file=file,
    )