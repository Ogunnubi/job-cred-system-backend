from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

from app.db.mongo import get_db
from app.models.application import JobApplication
from app.models.job import Job
from app.models.user import User
from app.schemas.job import JobIn, JobOut, JobApplicationIn, JobApplicationOut
from app.core.auth import get_current_user
from app.schemas.user import UserOut
from typing import List
from arq.connections import create_pool, RedisSettings
from app.core.config import REDIS_URL
import asyncio

router = APIRouter()

job_queue = asyncio.Queue()

@router.post("/", response_model=JobOut)
async def create_job(job_in: JobIn):
    job = Job(
        title=job_in.title,
        job_description=job_in.job_description,
        credits_required=job_in.credits_required,
        posted_by=None
    )
    await job.save()

    return JobOut(
        id=job.id,
        title=job.title,
        job_description=job.job_description,
        credits_required=job.credits_required,
        posted_by=None,
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


async def process_application_after_delay(application_id: str):
    try:
        await asyncio.sleep(300)

        db = get_db()

        result = await db.applications.update_one(
            {"_id": ObjectId(application_id), "status": "pending"},
            {"$set": {"status": "accepted"}}
        )

        if result.modified_count == 0:
            print(f"Application {application_id} was already processed or doesn't exist")


    except Exception as e:
        print(f"Error processing application {application_id}: {str(e)}")


@router.post("/{job_id}/apply")
async def apply_for_job(
        job_id: str,
        application: JobApplicationIn,
        current_user: UserOut = Depends(get_current_user)
):
    db = get_db()

    async with await db.client.start_session() as session:
        async with session.start_transaction():
            job = await Job.get_by_id(job_id)
            if not job:
                raise HTTPException(status_code=404, detail="Job not found")

            user = await User.get_by_id(current_user.id)
            try:
                await user.deduct_credits(job.credits_required)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_402_PAYMENT_REQUIRED,
                    detail=str(e)
                )

            new_application = JobApplication(
                job_id=job_id,
                user_id=current_user.id,
                proposal=application.proposal,
                status="pending"
            )
            await new_application.save()

    redis = await create_pool(RedisSettings.from_dsn(REDIS_URL))
    await redis.enqueue_job("process_application", new_application.id)

    return {
        "message": "Application submitted successfully",
        "application_id": new_application.id,
    }


@router.get("/applications/{application_id}", response_model=JobApplicationOut)
async def get_application(
        application_id: str,
        current_user: UserOut = Depends(get_current_user)
):
    application = await JobApplication.get_by_id(application_id)
    if not application or application.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Application not found")

    return JobApplicationOut(
        id=application.id,
        job_id=application.job_id,
        user_id=application.user_id,
        proposal=application.proposal,
        status=application.status,
        created_at=application.created_at
    )