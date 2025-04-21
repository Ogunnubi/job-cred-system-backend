# schemas/job.py
from pydantic import BaseModel
from typing import Optional

class JobIn(BaseModel):
    title: str
    job_description: str
    credits_required: int


class JobOut(BaseModel):
    id: str
    title: str
    job_description: str
    credits_required: int
    posted_by: Optional[str] = None
    created_at: Optional[str]

    class Config:
        from_attributes = True

class JobApplicationIn(BaseModel):
    proposal: str

class JobApplicationOut(BaseModel):
    id: str
    job_id: str
    user_id: str
    proposal: str
    status: str
    created_at: str