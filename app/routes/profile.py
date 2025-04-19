from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from app.db.mongo import get_db
from app.schemas.user import UserOut, ProfileUpdate
from app.models.user import User
from app.core.auth import get_current_user
from app.utils.jwt import create_access_token

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_my_profile(current_user: UserOut = Depends(get_current_user)):
    db = get_db()
    fresh_user_data = await db.users.find_one({"_id": ObjectId(current_user.id)})
    if not fresh_user_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return UserOut(
        id=str(fresh_user_data["_id"]),
        username=fresh_user_data["username"],
        email=fresh_user_data["email"],
        credits=fresh_user_data.get("credits", 0),
        created_at=fresh_user_data.get("created_at"),
        first_name=fresh_user_data.get("first_name"),
        last_name=fresh_user_data.get("last_name"),
        phone=fresh_user_data.get("phone")
    )


@router.put("/me", response_model=dict)
async def update_my_profile(
        profile_update: ProfileUpdate,
        current_user: UserOut = Depends(get_current_user)
):
    user = await User.get_by_id(current_user.id)
    await user.update_profile(
        profile_update.first_name,
        profile_update.last_name,
        profile_update.phone
    )
    updated_user = await User.get_by_id(current_user.id)

    token_data = {
        "username": updated_user.username,
        "email": updated_user.email,
        "id": updated_user.id,
    }
    new_token = create_access_token(token_data)

    return {
        "message": "Profile updated successfully",
        "access_token": new_token,
        "token_type": "Bearer"
    }