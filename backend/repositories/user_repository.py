from datetime import datetime
from backend.database.collections import collections
class UserRepository:
    async def create_user(
        self,
        username: str,
    ):
        document = {
            "username": username,
            "created_at": datetime.utcnow(),
        }
        result = await collections.users.insert_one(document)
        return str(result.inserted_id)
    async def get_user(
        self,
        username: str,
    ):
        return await collections.users.find_one(
            {"username": username}
        )
user_repository = UserRepository()