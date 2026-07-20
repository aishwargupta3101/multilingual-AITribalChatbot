from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile, HTTPException
from backend.config.settings import settings
from backend.document_processing.document_loader import document_loader
from backend.document_processing.text_splitter import document_splitter
from backend.rag.faiss_manager import faiss_manager
from backend.repositories.document_repository import document_repository

class UploadService:
    async def upload_document(
        self,
        session_id: str,
        file: UploadFile,
    ):
        extension = file.filename.split(".")[-1].lower()

        if extension not in settings.ALLOWED_FILE_TYPES.split(","):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file type."
            )
        content = await file.read()

        if len(content) > settings.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail="File exceeds maximum size."
            )
        document_id = str(uuid4())
        unique_filename = f"{document_id}.{extension}"
        upload_path = Path(settings.UPLOAD_DIR) / unique_filename
        vector_db_path = f"vector_db/{document_id}"
        upload_path.parent.mkdir(
            parents=True,
            exist_ok=True
        )
        upload_path.write_bytes(content)
        text = document_loader.load(
            str(upload_path)
        )
        documents = document_splitter.split(
            text=text,
            source=file.filename
        )
        faiss_manager.create_and_save(
            documents=documents,
            vector_db_path=vector_db_path
        )
        await document_repository.save_document(
            session_id=session_id,
            document_id=document_id,
            filename=unique_filename,
            original_filename=file.filename,
            file_path=str(upload_path),
            vector_db_path=vector_db_path,
            file_size=len(content),
            file_type=extension,
        )
        return {
            "status": "success",
            "message": "Document uploaded successfully.",
            "document_id": document_id,
            "filename": unique_filename,
            "vector_db_path": vector_db_path
        }
upload_service = UploadService()