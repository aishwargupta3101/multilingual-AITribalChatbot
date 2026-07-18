from fastapi import APIRouter,HTTPException
from backend.rag.retriever import retriever

router = APIRouter()

@router.get("/retriever-test")
async def retriever_test(question:str):
    try:
        documents = retriever.retrieve(
            question=question,
            vector_db_path="vector_db/test_document",
            k=3
        )
        return {
            "status":"success",
            "results":[
                doc.page_content
                for doc in documents
            ]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )