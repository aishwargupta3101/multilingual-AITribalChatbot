from fastapi.routing import APIRouter

from backend.llm.llama_service import llama_service
router = APIRouter()

@router.get("/llama-test")
async def test_llama():
    conversation =[
        {
            "role":"user",
            "content":"Hello"
        }
    ]
    answer = await llama_service.generate_response(
        conversation
    )
    return{
        "success":True,
        "answer":answer
    }
