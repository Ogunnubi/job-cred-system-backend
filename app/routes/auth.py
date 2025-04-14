from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import UserIn, UserOut, UserLogin
from app.models.user import User
from app.core.security import hash_password
from app.utils.jwt import create_access_token

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
        username= user_in.username,
        email=str(user_in.email),
        password=hashed_password,
        created_at=datetime.utcnow().isoformat()
    )
    await new_user.save()

    return UserOut(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        created_at=new_user.created_at
    )

@router.post("/login")
async def login(user_login: UserLogin):
    # 🔍 Find user by email
    user = await User.get_by_email(str(user_login.email))
    if not user or not await user.verify_password(user_login.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials."
        )

    token = create_access_token({"id": user.id, "email": user.email})

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email
        }
    }
