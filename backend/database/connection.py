from backend.config.logger import logger
from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase
from backend.config.settings import  settings

class MongoDB:
    def __init__(self):
        self.client:AsyncIOMotorClient | None =None
        self.database:AsyncIOMotorDatabase| None =None

    async def connect(self):
        self.client = AsyncIOMotorClient(
            settings.MONGODB_URI
        )
        self.database = self.client[
            settings.DATABASE_NAME
        ]
        logger.info("✅ MongoDB Connected")
    async  def disconnect(self):
        if self.client:
            self.client.close()
            logger.info("❌ MongoDB Disconnected")
mongodb = MongoDB()
