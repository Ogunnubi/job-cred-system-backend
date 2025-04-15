from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends, Response, Cookie
from jose import JWTError
from pydantic import EmailStr

from app.schemas.user import UserIn, UserOut, UserLogin
from app.models.user import User
from app.core.security import hash_password
from app.core.config import JWT_REFRESH_EXPIRATION_DAYS
from app.utils.jwt import create_access_token, create_refresh_token, verify_token

router = APIRouter()


# 📝 Signup route
@router.post("/signup", response_model=UserOut)
async def signup(user_in: UserIn):
    existing_user = await User.get_by_email(str(user_in.email))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists."
        )

    hashed_password = hash_password(user_in.password)

    new_user = User(
        username=user_in.username,
        email=str(user_in.email),
        password=hashed_password,
        credits=820,
        created_at=datetime.utcnow().isoformat()
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
    user = await User.get_by_email(str(user_login.email))
    if not user or not await user.verify_password(user_login.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"id": user.id, "email": user.email})
    refresh_token = create_refresh_token({"id": user.id})

    await user.add_refresh_token(refresh_token)
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=JWT_REFRESH_EXPIRATION_DAYS * 24 * 60 * 60,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "credits": user.credits
        }}


@router.post("/refresh")
async def refresh_token(refresh_token: str = Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    try:
        payload = verify_token(refresh_token)
        user = await User.get_by_id(payload["id"])

        if not user or not await user.is_valid_refresh_token(refresh_token):
            raise HTTPException(status_code=401, detail="Invalid or revoked token")

        new_access_token = create_access_token({"id": user.id, "email": user.email})
        return {"access_token": new_access_token, "token_type": "bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@router.post("/logout")
async def logout(response: Response, refresh_token: str = Cookie(None)):
    if refresh_token:
        payload = verify_token(refresh_token)
        user = await User.get_by_id(payload["id"])
        if user:
            await user.revoke_refresh_token(refresh_token)

    # Clear cookie
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}


