from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from backend.services.upload_service import upload_service
from backend.utils.response import ResponseBuilder
from backend.auth.auth_routes import get_current_user
from backend.repositories.session_repository import session_repository

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/")
async def upload_document(
    session_id: str = Form(...),
    language: str = Form(...),
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    session = await session_repository.get_session(session_id, current_user["id"])
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    result = await upload_service.upload_document(
        session_id=session_id,
        user_id=current_user["id"],
        language=language,
        file=file,
    )
    return ResponseBuilder.success(
        message="Document uploaded successfully.",
        data=result,
    )
