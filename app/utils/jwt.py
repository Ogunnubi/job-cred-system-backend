# 🎨 app/utils/jwt.py
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES
from app.schemas.user import UserOut

# 📅 Set token expiration
def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=JWT_EXPIRATION_MINUTES)) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

# 🔑 Validate JWT token
def verify_token(token: str) -> UserOut:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return UserOut(**payload)
    except JWTError:
        raise ValueError("Invalid token or expired.")