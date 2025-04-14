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


class UserOut(BaseModel):
    username: str
    email: EmailStr
    id: str
    created_at: Optional[str]

    class Config:
        orm_mode = True