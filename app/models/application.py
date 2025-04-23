from datetime import datetime, timezone
from bson import ObjectId
from typing import Optional
from app.db.mongo import get_db


class JobApplication:
    def __init__(self, job_id: str, user_id: str, proposal: str,
                 status: str = "pending", id: Optional[str] = None,
                 created_at: Optional[str] = None):
        self.job_id = job_id
        self.user_id = user_id
        self.proposal = proposal
        self.status = status
        self.id = id or str(ObjectId())
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()

    async def save(self):
        db = get_db()
        await db.applications.insert_one({
            "_id": ObjectId(self.id),
            "job_id": self.job_id,
            "user_id": self.user_id,
            "proposal": self.proposal,
            "status": self.status,
            "created_at": self.created_at
        })

    @staticmethod
    async def get_by_id(application_id: str):
        db = get_db()
        app_data = await db.applications.find_one({"_id": ObjectId(application_id)})
        if app_data:
            return JobApplication(
                job_id=app_data["job_id"],
                user_id=app_data["user_id"],
                proposal=app_data["proposal"],
                status=app_data["status"],
                id=str(app_data["_id"]),
                created_at=app_data.get("created_at")
            )
        return None