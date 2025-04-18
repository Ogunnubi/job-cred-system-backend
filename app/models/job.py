# models/job.py
from bson import ObjectId
from typing import Optional
from datetime import datetime

from fastapi import HTTPException
from starlette import status

from app.db.mongo import get_db

class Job:
    def __init__(self, title: str, job_description: str, credits_required: int, posted_by: str,
                 id: Optional[str] = None, created_at: Optional[str] = None):
        self.title = title
        self.job_description = job_description
        self.credits_required = credits_required
        self.posted_by = posted_by
        self.id = id or str(ObjectId())
        self.created_at = created_at or datetime.utcnow().isoformat()

    def to_dict(self):
        return {
            "_id": ObjectId(self.id) if self.id else ObjectId(),
            "title": self.title,
            "job_description": self.job_description,
            "credits_required": self.credits_required,
            "posted_by": self.posted_by,
            "created_at": self.created_at or datetime.utcnow().isoformat()
        }

    async def save(self):
        db = get_db()
        try:
            job_dict = self.to_dict()
            print("Attempting to save job:", job_dict)  # Debug log
            result = await db.jobs.insert_one(job_dict)
            self.id = str(result.inserted_id)
            print("Job saved successfully, ID:", self.id)  # Debug log
            return self
        except Exception as e:
            print("Error saving job:", str(e))  # Debug log
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save job to database"
            )

    @staticmethod
    async def get_all():
        db = get_db()
        jobs = []
        async for job_data in db.jobs.find():
            jobs.append(Job(
                title=job_data["title"],
                job_description=job_data["job_description"],
                credits_required=job_data["credits_required"],
                posted_by=job_data["posted_by"],
                id=str(job_data["_id"]),
                created_at=job_data.get("created_at")
            ))
        return jobs

    @staticmethod
    async def get_by_id(job_id: str):
        db = get_db()
        job_data = await db.jobs.find_one({"_id": ObjectId(job_id)})
        if job_data:
            return Job(
                title=job_data["title"],
                job_description=job_data["job_description"],
                credits_required=job_data["credits_required"],
                posted_by=job_data["posted_by"],
                id=str(job_data["_id"]),
                created_at=job_data.get("created_at")
            )
        return None