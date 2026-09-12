from fastapi import APIRouter, UploadFile, File, Form

from backend.services.upload_service import upload_service
from backend.utils.response import ResponseBuilder

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)
@router.post("/")
async def upload_document(
    session_id: str = Form(...),
    language: str = Form(...),
    file: UploadFile = File(...)
):
    result = await upload_service.upload_document(
        session_id=session_id,
        language=language,
        file=file
    )
    return ResponseBuilder.success(
        message="Document uploaded successfully.",
        data=result
    )
