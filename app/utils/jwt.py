from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.core.config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES, JWT_REFRESH_EXPIRATION_DAYS

def create_access_token(data: dict) -> str:
    expires_delta = timedelta(minutes=JWT_EXPIRATION_MINUTES)
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    expires_delta = timedelta(days=JWT_REFRESH_EXPIRATION_DAYS)
    to_encode = data.copy()
    expire = datetime.now() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Invalid token")