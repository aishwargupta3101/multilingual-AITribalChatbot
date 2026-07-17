from fastapi import APIRouter
from backend.document_processing.document_loader import document_loader
from backend.document_processing.text_splitter import document_splitter
from backend.rag.faiss_manager import faiss_manager

router = APIRouter()

@router.get("/faiss-test")
async def faiss_test(file_path :str):
    text = document_loader.load(file_path)
    chunks = document_splitter.split(text)
    faiss_manager.create_vector_store(
        chunks,
        save_path="vector_db/test_document"
    )
    return{
        "chunks":len(chunks),
        "status" : "Vector DB Created"
    }