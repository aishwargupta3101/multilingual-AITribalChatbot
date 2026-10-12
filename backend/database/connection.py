from backend.config.logger import logger
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase
from backend.config.settings import  settings

class MongoDB:
    def __init__(self):
        self.client:AsyncIOMotorClient | None =None
        self.database:AsyncIOMotorDatabase| None =None

    async def connect(self):
        try:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=10000
            )
            self.database = self.client[settings.DATABASE_NAME]
            await self.client.admin.command("ping")
            logger.info("MongoDB Connected Successfully")
        except Exception as e:
            logger.error(f"MongoDB Connection Failed: {e}")

            if self.client:
                self.client.close()
                self.client = None
                self.database = None

            raise
    async  def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("❌ MongoDB Disconnected")
mongodb = MongoDB()
