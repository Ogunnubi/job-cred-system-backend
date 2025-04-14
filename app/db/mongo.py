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
        self.client = AsyncIOMotorClient(MONGO_URI)
        self.db = self.client[DB_NAME]
        print("✅ Connected to MongoDB")

    async def close(self):
        if self.client:
            await self.client.close()
            print("❌ Disconnected from MongoDB")


# Create a single instance
mongodb = MongoDB()


def get_db():
    return mongodb.db