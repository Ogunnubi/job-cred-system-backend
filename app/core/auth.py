from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import SECRET_KEY, JWT_ALGORITHM
from app.models.user import User
from app.schemas.user import UserOut

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserOut:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")

        # Always fetch fresh user data from database
        user = await User.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        return UserOut(
            id=user.id,
            username=user.username,
            email=user.email,
            credits=user.credits,
            created_at=user.created_at,
            first_name=user.first_name,
            last_name=user.last_name,
            phone=user.phone
        )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")