from fastapi import APIRouter, Depends, HTTPException, status
from app.models.job import Job
from app.schemas.job import JobIn, JobOut
from app.core.auth import get_current_user
from app.schemas.user import UserOut
from typing import List

router = APIRouter()


@router.post("/", response_model=JobOut)
async def create_job(
        job_in: JobIn,
        current_user: UserOut = Depends(get_current_user)
):
    if current_user.credits < job_in.credits_required:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough credits to post this job"
        )

    job = Job(
        title=job_in.title,
        job_description=job_in.job_description,
        credits_required=job_in.credits_required,
        posted_by=current_user.id  # Track who posted the job
    )
    await job.save()

    return JobOut(
        id=job.id,
        title=job.title,
        job_description=job.job_description,
        credits_required=job.credits_required,
        posted_by=job.posted_by,
        created_at=job.created_at
    )


@router.get("/{job_id}", response_model=JobOut)
async def get_job_by_id(
        job_id: str,
        current_user: UserOut = Depends(get_current_user)
):
    job = await Job.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found"
        )

    return JobOut(
        id=job.id,
        title=job.title,
        job_description=job.job_description,
        credits_required=job.credits_required,
        posted_by=job.posted_by,
        created_at=job.created_at
    )

@router.get("/", response_model=List[JobOut])
async def get_all_jobs(current_user: UserOut = Depends(get_current_user)):
    jobs = await Job.get_all()
    return [JobOut(
        id=job.id,
        title=job.title,
        job_description=job.job_description,
        credits_required=job.credits_required,
        posted_by=job.posted_by,
        created_at=job.created_at
    ) for job in jobs]