from pydantic import BaseModel, EmailStr
from typing import Optional

class UserIn(BaseModel):
    username: str
    email: EmailStr
    password: str

    class Config:
        min_anystr_length = 1
        anystr_strip_whitespace = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str

class UserOut(BaseModel):
    username: str
    email: EmailStr
    id: str
    credits: int
    created_at: Optional[str]
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

    class Config:
        orm_mode = True

class ProfileUpdate(BaseModel):
    first_name: str
    last_name: str
    phone: str