from bson import ObjectId
from typing import Optional
from app.db.mongo import get_db
from app.models.credit import CreditTransaction
from app.schemas.credit import TransactionType


class User:
    def __init__(self, username: str, email: str, password: str, id: Optional[str] = None,
                 created_at: Optional[str] = None, credits: int = 820, first_name: Optional[str] = None,
             last_name: Optional[str] = None, phone: Optional[str] = None):
        self.username = username
        self.email = email
        self.password = password
        self.id = id or str(ObjectId())
        self.created_at = created_at
        self.credits = credits
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone

    def to_dict(self):
        return {
            "_id": ObjectId(self.id) if self.id else ObjectId(),
            "username": self.username,
            "email": self.email,
            "password": self.password,
            "created_at": self.created_at,
            "credits": self.credits,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "phone": self.phone
        }

    async def update_profile(self, first_name: str, last_name: str, phone: str):
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        db = get_db()
        await db.users.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone
            }}
        )

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

    async def set_password(self, new_password: str):
        from app.core.security import hash_password
        self.password = hash_password(new_password)
        db = get_db()
        await db.users.update_one(
            {"_id": ObjectId(self.id)},
            {"$set": {"password": self.password}}
        )

    @staticmethod
    async def create_reset_token(email: str) -> str:
        from app.utils.jwt import create_reset_token
        user = await User.get_by_email(email)
        if not user:
            raise ValueError("User not found")
        return create_reset_token({"id": user.id})

    @staticmethod
    async def reset_password(token: str, new_password: str):
        from app.utils.jwt import verify_reset_token
        payload = verify_reset_token(token)
        user = await User.get_by_id(payload["id"])
        if not user:
            raise ValueError("Invalid token")
        await user.set_password(new_password)

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
        db = get_db()

        user = await  db.users.find_one({"_id": ObjectId(self.id)})
        if not user:
            raise ValueError("User not Found")
        if user.get("credits", 0) < amount:
            raise ValueError("Not Enough Credits")
        result = await db.users.update_one(
            {"_id": ObjectId(self.id), "credits": {"$gte": amount}},
            {"$inc": {"credits": -amount}}
        )
        if result.modified_count == 0:
            raise ValueError("Not enough credits or user not found")

        self.credits -= amount

    async def add_credits(
            self,
            amount: int,
            transaction_type: TransactionType.TOPUP,
            description: str
    ):
        db = get_db()

        tx = CreditTransaction(
            user_id=self.id,
            amount=amount,
            transaction_type=TransactionType.TOPUP,
            description=description
        )
        await tx.save()

        await db.users.update_one(
            {"_id": ObjectId(self.id)},
            {"$inc": {"credits": amount}}
        )


