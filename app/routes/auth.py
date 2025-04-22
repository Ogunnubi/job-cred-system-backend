from datetime import datetime

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, Response, Cookie
from jose import JWTError

from app.db.mongo import get_db
from app.schemas.user import UserIn, UserOut, UserLogin, PasswordResetConfirm, PasswordResetRequest
from app.models.user import User
from app.core.security import hash_password
from app.core.config import JWT_REFRESH_EXPIRATION_DAYS
from app.utils.jwt import create_access_token, create_refresh_token, verify_token

router = APIRouter()

@router.post("/signup", response_model=UserOut)
async def signup(user_in: UserIn):
    existing_user = await User.get_by_email(str(user_in.email))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists."
        )

    hashed_password = hash_password(user_in.password)

    new_user = User(
        username=user_in.username,
        email=str(user_in.email),
        password=hashed_password,
        credits=820,
        created_at=datetime.now().isoformat()
    )
    await new_user.save()

    return UserOut(
        id=new_user.id,
        username=new_user.username,
        credits=new_user.credits,
        email=new_user.email,
        created_at=new_user.created_at
    )


@router.post("/login")
async def login(user_login: UserLogin, response: Response):
    # First get user by email
    user = await User.get_by_email(str(user_login.email))
    if not user or not await user.verify_password(user_login.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create tokens with just user ID
    token_data = {
        "username": user.username,
        "email": user.email,
        "id": user.id,
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)

    # Store refresh token
    await user.add_refresh_token(refresh_token)

    # Set cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # True in production
        samesite="lax",
        max_age=JWT_REFRESH_EXPIRATION_DAYS * 60 * 60 * 24,
    )

    db = get_db()
    fresh_user = await db.users.find_one({"_id": ObjectId(user.id)})
    if not fresh_user:
        raise HTTPException(status_code=500, detail="User data not found")

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "user": {
            "id": str(fresh_user["_id"]),
            "email": fresh_user["email"],
            "credits": fresh_user["credits"]  # This will be current
        }
    }


@router.get("/refresh")
async def refresh_token(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = verify_token(refresh_token)
        user = await User.get_by_id(payload["id"])

        if not user or not await user.is_valid_refresh_token(refresh_token):
            raise HTTPException(status_code=401, detail="Invalid or revoked token")

        token_data = {
            "username": user.username,
            "email": user.email,
            "id": user.id,
        }

        new_access_token = create_access_token(token_data)
        return {"access_token": new_access_token, "token_type": "Bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/request-password-reset")
async def request_password_reset(
    request: PasswordResetRequest,
):
    try:
        reset_token = await User.create_reset_token(str(request.email))
        # In production, you would send an email here
        print(f"Password reset token: {reset_token}")  # For testing
        return {"message": "If email exists, reset link has been sent"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/reset-password")
async def reset_password(request: PasswordResetConfirm):
    try:
        await User.reset_password(request.token, request.new_password)
        return {"message": "Password reset successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/logout")
async def logout(response: Response, refresh_token: str = Cookie(None)):
    if refresh_token:
        payload = verify_token(refresh_token)
        user = await User.get_by_id(payload["id"])
        if user:
            await user.revoke_refresh_token(refresh_token)


    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}


