from datetime import datetime
from backend.database.collections import collections


class ChatRepository:
    async def save_message(self, session_id: str, user_id: str, role: str,
                           message: str, language: str):
        document = {
            "session_id": session_id,
            "user_id": str(user_id),
            "role": role,
            "message": message,
            "language": language,
            "created_at": datetime.utcnow(),
        }
        result = await collections.chat_history.insert_one(document)
        return str(result.inserted_id)

    async def get_chat_history(self, session_id: str, user_id: str):
        cursor = collections.chat_history.find(
            {"session_id": session_id, "user_id": str(user_id)}
        ).sort("created_at", 1)
        history = await cursor.to_list(length=500)
        for message in history:
            message["_id"] = str(message["_id"])
        return history

    async def get_recent_message(self, session_id: str, user_id: str, limit: int = 8):
        cursor = (
            collections.chat_history
            .find({"session_id": session_id, "user_id": str(user_id)})
            .sort("created_at", -1)
            .limit(limit)
        )
        messages = await cursor.to_list(length=limit)
        messages.reverse()
        for message in messages:
            message["_id"] = str(message["_id"])
        return messages

    async def get_recent_sessions(self, user_id: str, limit: int = 10):
        pipeline = [
            {"$match": {"user_id": str(user_id)}},
            {"$sort": {"created_at": -1}},
            {"$group": {
                "_id": "$session_id",
                "last_message": {"$first": "$message"},
                "last_activity": {"$first": "$created_at"},
                "language": {"$first": "$language"},
                "messages": {"$push": {
                    "role": "$role", "message": "$message",
                    "language": "$language", "created_at": "$created_at"
                }}
            }},
            {"$sort": {"last_activity": -1}},
            {"$limit": max(1, min(int(limit), 100))}
        ]
        cursor = collections.chat_history.aggregate(pipeline)
        return await cursor.to_list(length=max(1, min(int(limit), 100)))


chat_repository = ChatRepository()
