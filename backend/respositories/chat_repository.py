from backend.respositories.base_repository import BaseRepository
class ChatRepository(BaseRepository):
    async  def save_chat(self,data):
        return data
    async def get_chat(self,session_id):
        return []