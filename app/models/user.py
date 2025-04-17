from bson import ObjectId
from typing import Optional
from app.db.mongo import get_db


class User:
    def __init__(self, username: str, email: str, password: str, id: Optional[str] = None,
                 created_at: Optional[str] = None, credits: int = 820):
        self.username = username
        self.email = email
        self.password = password
        self.id = id or str(ObjectId())
        self.created_at = created_at
        self.credits = credits

    def to_dict(self):
        return {
            "_id": ObjectId(self.id) if self.id else ObjectId(),
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at,
            "credits": self.credits
        }

    async def save(self):
        db = get_db()
        result = await db.users.insert_one(self.to_dict())
        self.id = str(result.inserted_id)

    @staticmethod
    async def get_by_email(email: str):
        db = get_db()
        user_data = await db.users.find_one({"email": email})
        if user_data:
            return User(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
                id=str(user_data["_id"]),
                created_at=user_data.get("created_at")
            )
        return None

    @staticmethod
    async def get_by_id(user_id: str):
        db = get_db()
        user_data = await db.users.find_one({"_id": ObjectId(user_id)})
        if user_data:
            return User(
                username=user_data["username"],
                email=user_data["email"],
                password=user_data["password"],
                id=str(user_data["_id"]),
                created_at=user_data.get("created_at")
            )
        return None

    async def verify_password(self, password: str) -> bool:
        from app.core.security import verify_password
        return verify_password(password, self.password)

    async def add_refresh_token(self, token: str):
        db = get_db()
        await db.users.update_one(
            {"_id": ObjectId(self.id)},
            {"$push": {"refresh_tokens": token}}
        )

    async def is_valid_refresh_token(self, token: str) -> bool:
        db = get_db()
        user_data = await db.users.find_one(
            {"_id": ObjectId(self.id), "refresh_tokens": token}
        )
        return user_data is not None

    async def revoke_refresh_token(self, token: str):
        db = get_db()
        await db.users.update_one(
            {"_id": ObjectId(self.id)},
            {"$pull": {"refresh_tokens": token}}
        )

    async def deduct_credits(self, amount: int):
        if self.credits < amount:
            raise ValueError("Not enough credits")
        self.credits -= amount
        db = get_db()
        await db.users.update_one(
            {"_id": ObjectId(self.id)},
            {"$inc": {"credits": -amount}}
        )
