from fastapi import APIRouter, HTTPException
from backend.rag.rag_service import rag_service

router = APIRouter()

@router.get("/rag-test")
async def rag_test(question: str):
    try:
        result = await rag_service.generate_answer(
            question=question
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )