from fastapi import APIRouter
from backend.document_processing.text_splitter import document_splitter
from backend.document_processing.document_loader import document_loader
from backend.rag.rag_service import rag_service
router = APIRouter()
@router.get("/document-test")
async def document_test(file_path :str):
    text = document_loader.load(
        file_path
    )
    chunks = document_splitter.split(text)
    embeddings = rag_service.create_embeddings(
        chunks
    )
    return {
        "chunks":len(chunks),
        "embedding_dimension":len(embeddings[0]),
        "total_embeddings" : len(embeddings)
    }