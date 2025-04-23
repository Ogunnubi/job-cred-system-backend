from fastapi import APIRouter, Depends, HTTPException
from app.models.user import User
from app.models.credit import CreditTransaction
from app.schemas.credit import (
    CreditTransactionOut,
    CreditPackage,
    CreditTopupRequest
)
from app.schemas.user import UserOut
from app.core.auth import get_current_user
from app.services.credit_service import CreditService
from typing import List

router = APIRouter()


@router.get("/history", response_model=List[CreditTransactionOut])
async def get_credit_history(
        current_user: UserOut = Depends(get_current_user),
        limit: int = 100
):
    transactions = await CreditTransaction.get_by_user(current_user.id, limit)
    if not transactions:
        raise HTTPException(
            status_code=404,
            detail="No transactions found"
        )
    return transactions


@router.post("/topup")
async def topup_credits(
        request: CreditTopupRequest,
        current_user: UserOut = Depends(get_current_user)
):
    package = CreditService.get_package_details(request.package)

    user = await User.get_by_id(current_user.id)
    await user.add_credits(
        amount=package["credits"],
        transaction_type="topup",
        description=f"Purchased {request.package.value} package ({package['credits']} credits)"
    )

    return {
        "message": f"Successfully added {package['credits']} credits",
        "package": request.package.value
    }


@router.get("/packages")
async def get_credit_packages():
    return [
        {
            "name": package.value,
            "credits": CreditService.PACKAGES[package]["credits"],
            "usd": CreditService.PACKAGES[package]["usd"]
        }
        for package in CreditPackage
    ]