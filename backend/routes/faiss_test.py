from fastapi import APIRouter,HTTPException
from backend.document_processing.document_loader import document_loader
from backend.document_processing.text_splitter import document_splitter
from backend.rag.faiss_manager import faiss_manager

router = APIRouter()

@router.get("/faiss-test")
async def faiss_test(file_path :str):
    try:
        text = document_loader.load(file_path)
        chunks = document_splitter.split(text)
        faiss_manager.create_and_save(
            chunks,
            save_path="vector_db/test_document"
        )
        return{
            "chunks":len(chunks),
            "status" : "Success",
            "vector_db":"vector_db/test_document"
    }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)

    )