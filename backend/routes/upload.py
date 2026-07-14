from pathlib import Path
from fastapi import APIRouter,UploadFile,File
router = APIRouter()

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True
)
@router.post("/")
async def upload_file(
    file:UploadFile=File(...)
):
    destination = UPLOAD_DIR /file.filename
    with open(destination,"wb") as f:
        f.write(await file.read())
    return{
        "filename":file.filename,
        "status":"uploaded"
    }