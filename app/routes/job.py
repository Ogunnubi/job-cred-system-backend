from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks

from app.db.mongo import get_db
from app.models.application import JobApplication
from app.models.credit import CreditTransaction
from app.models.job import Job
from app.models.user import User
from app.schemas.credit import TransactionType
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
        posted_by=job_in.posted_by
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

            existing_application = await db.applications.find_one({
                "job_id": job_id,
                "user_id": current_user.id
            })
            if existing_application:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Application Already Sent"
                )

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

            tx = CreditTransaction(
                user_id=current_user.id,
                amount=-job.credits_required,
                transaction_type=TransactionType.JOB_APPLICATION,
                description=f"Applied for job: {job.title} (ID: {job_id})",
                job_id=job_id
            )
            await tx.save()

    # redis = await create_pool(RedisSettings.from_dsn(REDIS_URL))
    # await redis.enqueue_job("process_application", new_application.id)
    return {
        "message": "Application submitted successfully",
        "application_id": new_application.id,
    }


@router.put("/applications/{application_id}", response_model=JobApplicationOut)
async def update_application(
        application_id: str,
        updated_application: JobApplicationIn,
        current_user: UserOut = Depends(get_current_user)
):
    db = get_db()

    application = await db.applications.find_one({
        "_id": ObjectId(application_id),
        "user_id": current_user.id
    })

    if not application:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or not owned by user"
        )

    await db.applications.update_one(
        {"_id": ObjectId(application_id)},
        {"$set": {"proposal": updated_application.proposal}}
    )

    updated = await db.applications.find_one({"_id": ObjectId(application_id)})
    return JobApplicationOut(
        id=str(updated["_id"]),
        job_id=updated["job_id"],
        user_id=updated["user_id"],
        proposal=updated["proposal"],
        status=updated["status"],
        created_at=updated["created_at"]
    )


@router.delete("/applications/{application_id}")
async def delete_application(
        application_id: str,
        current_user: UserOut = Depends(get_current_user)
):
    db = get_db()

    result = await db.applications.delete_one({
        "_id": ObjectId(application_id),
        "user_id": current_user.id
    })

    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Application not found or not owned by user"
        )

    return {"message": "Application deleted successfully"}


@router.get("/applications/user", response_model=List[JobApplicationOut])
async def get_user_applications(
        current_user: UserOut = Depends(get_current_user)
):
    db = get_db()

    applications = []
    async for app_data in db.applications.find({"user_id": current_user.id}):
        applications.append(JobApplicationOut(
            id=str(app_data["_id"]),
            job_id=app_data["job_id"],
            user_id=app_data["user_id"],
            proposal=app_data["proposal"],
            status=app_data["status"],
            created_at=app_data.get("created_at")
        ))

    return applications