from datetime import datetime

from backend.database.collections import collections
class ChatRepository:
    async def save_message(
        self,
        session_id: str,
        role: str,
        message: str,
        language: str,
    ):
        document = {
            "session_id": session_id,
            "role": role,
            "message": message,
            "language": language,
            "created_at": datetime.utcnow(),
        }
        result = await collections.chat_history.insert_one(document)
        return str(result.inserted_id)
    async def get_chat_history(
        self,
        session_id: str,
    ):
        cursor = collections.chat_history.find(
            {"session_id": session_id}
        )
        history = await cursor.to_list(length=100)
        for message in history:
            message["_id"]= str(message["_id"])
        return history

    async def get_recent_message(
        self,
        session_id: str,
        limit:int =8,
    ):
        cursor =(
            collections.chat_history
            .find({"session_id": session_id})
            .sort("created_at",-1)
            .limit(limit)
        )
        messages = await cursor.to_list(length=limit)
        messages.reverse()
        for message in messages:
            message["_id"] =str(message["_id"])
        return messages

chat_repository = ChatRepository()