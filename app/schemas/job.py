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
    created_at: Optional[str]

    class Config:
        orm_mode = True