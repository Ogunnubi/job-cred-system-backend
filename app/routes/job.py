# routes/job.py
from fastapi import APIRouter, Depends, HTTPException, status
from app.models.job import Job
from app.schemas.job import JobIn, JobOut
from app.core.auth import get_current_user
from app.schemas.user import UserOut
from typing import List

router = APIRouter()

@router.post("/", response_model=JobOut)
async def create_job(job_in: JobIn, current_user: UserOut = Depends(get_current_user)):
    job = Job(
        title=job_in.title,
        job_description=job_in.job_description,
        credits_required=job_in.credits_required
    )
    await job.save()
    return JobOut(
        id=job.id,
        title=job.title,
        job_description=job.job_description,
        credits_required=job.credits_required,
        created_at=job.created_at
    )

@router.get("/", response_model=List[JobOut])
async def get_all_jobs():
    jobs = await Job.get_all()
    return [JobOut(
        id=job.id,
        title=job.title,
        job_description=job.job_description,
        credits_required=job.credits_required,
        created_at=job.created_at
    ) for job in jobs]