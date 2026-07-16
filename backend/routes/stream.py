from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from backend.llm.llama_service import llama_service

router =APIRouter()

@router.get("/stream")
async def stream():
    conversation =[
        {
            "role" : "user",
            "content": "Tell me about India."
        }
    ]
    async def generator():
        async for token in llama_service.stream_response(
            conversation
        ):
            yield token
    return StreamingResponse(
        generator(),
        media_type="text/plain",

    )
