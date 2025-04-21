from arq.connections import RedisSettings
from arq.worker import Worker
from app.core.config import REDIS_URL
from app.db.mongo import mongodb
from bson import ObjectId
import asyncio
import logging

logger = logging.getLogger(__name__)


async def process_application(application_id: str):
    try:
        logger.info(f"Starting to process application {application_id}")

        if mongodb.db is None:
            await mongodb.connect()

        db = mongodb.db

        for i in range(10):
            await asyncio.sleep(30)
            logger.info(f"Processing {application_id}... {i + 1}/10 checks completed")

        result = await db.applications.update_one(
            {"_id": ObjectId(application_id), "status": "pending"},
            {"$set": {"status": "accepted"}}
        )

        if result.modified_count == 1:
            logger.info(f"Successfully updated application {application_id} to 'accepted'")
            return True
        else:
            logger.warning(f"No pending application found with ID {application_id}")
            return False

    except Exception as e:
        logger.error(f"Failed to process application {application_id}: {str(e)}")
        raise
    finally:
        pass


async def startup():
    try:
        if mongodb.db is None:
            await mongodb.connect()
        logger.info("Worker connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


async def shutdown():
    try:
        if mongodb.db is not None:
            await mongodb.close()
        logger.info("Worker disconnected from MongoDB")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

worker_settings = {
    "functions": [process_application],
    "redis_settings": RedisSettings.from_dsn(REDIS_URL),
    "on_startup": startup,
    "on_shutdown": shutdown,
    "job_timeout": 600,
    "max_tries": 3,
    "retry_jobs": True
}


async def create_worker():
    return Worker(**worker_settings)