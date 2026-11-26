from datetime import datetime
from backend.database.collections import collections


class SessionRepository:
    async def create_session(self, session_id: str, user_id: str):
        # A session ID is owned by exactly one account. Never adopt legacy
        # ownerless sessions automatically.
        existing = await collections.sessions.find_one({"session_id": session_id})
        if existing:
            if str(existing.get("user_id", "")) != str(user_id):
                return None
            return existing

        document = {
            "session_id": session_id,
            "user_id": str(user_id),
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "status": "active",
        }
        result = await collections.sessions.insert_one(document)
        document["_id"] = str(result.inserted_id)
        return document

    async def update_activity(self, session_id: str, user_id: str):
        await collections.sessions.update_one(
            {"session_id": session_id, "user_id": str(user_id)},
            {"$set": {"last_activity": datetime.utcnow()}},
        )

    async def get_session(self, session_id: str, user_id: str):
        session = await collections.sessions.find_one(
            {"session_id": session_id, "user_id": str(user_id)}
        )
        if session:
            session["_id"] = str(session["_id"])
        return session

    async def get_all_session(self, user_id: str):
        cursor = collections.sessions.find({"user_id": str(user_id)})
        sessions = await cursor.to_list(length=100)
        for session in sessions:
            session["_id"] = str(session["_id"])
        return sessions

    async def delete_session(self, session_id: str, user_id: str):
        result = await collections.sessions.delete_one(
            {"session_id": session_id, "user_id": str(user_id)}
        )
        # Delete associated user-owned chat/document metadata only after
        # matching an owned session.
        if result.deleted_count:
            await collections.chat_history.delete_many(
                {"session_id": session_id, "user_id": str(user_id)}
            )
            await collections.documents.delete_many(
                {"session_id": session_id, "user_id": str(user_id)}
            )
        return result.deleted_count


session_repository = SessionRepository()
