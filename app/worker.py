from arq.connections import RedisSettings
from arq.worker import Worker
from app.core.config import REDIS_URL
from app.db.mongo import get_db
from bson import ObjectId
import asyncio


async def process_application(ctx, application_id: str):

    db = get_db()
    await asyncio.sleep(300)

    result = await db.applications.update_one(
        {"_id": ObjectId(application_id), "status": "pending"},
        {"$set": {"status": "accepted"}}
    )

    if result.modified_count == 0:
        print(f"Application {application_id} was already processed or doesn't exist")
    else:
        print(f"Application {application_id} accepted")

worker_settings = {
    "functions": [process_application],
    "redis_settings": RedisSettings.from_dsn(REDIS_URL)
}


async def create_worker():
    return Worker(**worker_settings)