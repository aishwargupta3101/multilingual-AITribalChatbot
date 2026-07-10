from datetime import datetime
from backend.schemas.chat import ChatRequest
from backend.utils.response import ResponseBuilder

class ChatService:

    async def process_chat(
            self,
            request:ChatRequest
    ):
            answer = f"You asked:{request.question}"
            return ResponseBuilder.success(
                    message="chat processed successfully",
                    data={
                        "answer": answer,
                        "language" : request.language,
                        "timestamp" :str(datetime.now())
                    }

                )