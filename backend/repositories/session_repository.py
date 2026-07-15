from datetime import datetime
from backend.database.collections import collections

class SessionRepository:
    async def create_session(
        self,
        session_id:str,
    ):
        existing= await collections.sessions.find_one(
            {"session_id" : session_id}
        )
        if existing:
            return existing
        document = {
            "session_id":session_id,
            "created_at": datetime.utcnow(),
            "last_activity":datetime.utcnow(),
            "status":"active"
        }
        result = await collections.sessions.insert_one(document)

        return str(result.inserted_id)
    async  def update_activity(self,session_id:str):
        await collections.sessions.update_one(
            {"session_id":session_id},
            {
                "$set":{
                    "last_activity" :  datetime.utcnow()
                }
            }
        )
    async def get_session(
        self,
        session_id:str,
    ):
        session = await collections.sessions.find_one(
            {
                "session_id":session_id
            }
        )
        if session:
            session["_id"] = str(session["_id"])
        return session

    async def get_all_session(self):
        cursor =collections.sessions.find()
        sessions= await cursor.to_list(length=100)
        for session in sessions:
            session["_id"] = str(session["_id"])
        return sessions
    async def delete_session(self,session_id:str):
        await collections.sessions.delete_one(
            {"session_id": session_id}
        )
session_repository = SessionRepository()