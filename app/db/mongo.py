from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI: str = os.getenv("MONGO_URI")
DB_NAME: str = os.getenv("DB_NAME")


class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None

    async def connect(self):
        if not self.client:
            self.client = AsyncIOMotorClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            print("✅ Connected to MongoDB")
        return self.db

    async def close(self):
        if self.client:
            await self.client.close()
            self.client = None
            self.db = None
            print("❌ Disconnected from MongoDB")

    def get_db(self):
        if not self.db:
            raise RuntimeError("Database not connected")
        return self.db


mongodb = MongoDB()


def get_db():
    return mongodb.db