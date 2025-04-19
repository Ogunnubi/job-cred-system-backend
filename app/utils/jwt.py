from datetime import datetime, timedelta, timezone  # Import timezone
from jose import JWTError, jwt
from app.core.config import SECRET_KEY, JWT_ALGORITHM, JWT_EXPIRATION_MINUTES, JWT_REFRESH_EXPIRATION_DAYS

def create_access_token(data: dict) -> str:
    expires_delta = timedelta(minutes=JWT_EXPIRATION_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta

    token_data = {
        "id": str(data["id"]),
        "username": data["username"],
        "email": data["email"],
        "exp": expire
    }

    return jwt.encode(token_data, SECRET_KEY, algorithm=JWT_ALGORITHM)

def create_refresh_token(data: dict) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_REFRESH_EXPIRATION_DAYS)

    token_data = {
        "id": str(data["id"]),
        "username": data["username"],
        "email": data["email"],
        "exp": expire
    }

    return jwt.encode(token_data, SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if not all(key in payload for key in ["id", "username", "email"]):
            raise ValueError("Token missing required claims")
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")

def create_reset_token(data: dict) -> str:
    expires_delta = timedelta(minutes=JWT_EXPIRATION_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta

    token_data = {
        "id": str(data["id"]),
        "username": data["username"],
        "email": data["email"],
        "exp": expire
    }

    return jwt.encode(token_data, SECRET_KEY, algorithm=JWT_ALGORITHM)

def verify_reset_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[JWT_ALGORITHM])
        if "id" not in payload:
            raise ValueError("Token missing required claims")
        return payload
    except JWTError as e:
        raise ValueError(f"Invalid or expired token: {str(e)}")