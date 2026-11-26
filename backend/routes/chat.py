from backend.services.chat_service import ChatService
from fastapi import APIRouter, Depends
from backend.api.dependencies import get_chat_service
from backend.auth.auth_routes import get_current_user
from backend.schemas.chat import ChatRequest
import asyncio
import json
from fastapi.responses import StreamingResponse

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post("/")
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    return await chat_service.process_chat(request, user_id=current_user["id"])


@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service),
):
    queue = asyncio.Queue()

    async def on_token(token):
        await queue.put({"type": "token", "content": token})

    async def process_request():
        try:
            result = await chat_service.process_chat(
                request, on_token=on_token, user_id=current_user["id"]
            )
            await queue.put({"type": "complete", "data": result})
        except Exception:
            # Do not expose internal exception details to clients.
            await queue.put({"type": "error", "message": "Chat processing failed."})
        finally:
            await queue.put(None)

    async def event_generator():
        task = asyncio.create_task(process_request())
        try:
            while True:
                event = await queue.get()
                if event is None:
                    break
                yield f"data: {json.dumps(event, ensure_ascii=False)}\n\n"
        finally:
            if not task.done():
                task.cancel()

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
