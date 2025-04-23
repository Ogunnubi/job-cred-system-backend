from datetime import datetime
from bson import ObjectId
from app.db.mongo import get_db
from app.schemas.credit import TransactionType

class CreditTransaction:
    def __init__(self, user_id: str, amount: int, transaction_type: TransactionType,
                 description: str, job_id: str = None, id: str = None,
                 created_at: str = None):
        self.user_id = user_id
        self.amount = amount
        self.transaction_type = transaction_type
        self.description = description
        self.job_id = job_id
        self.id = id or str(ObjectId())
        self.created_at = created_at or datetime.utcnow().isoformat()

    async def save(self):
        db = get_db()
        await db.credit_transactions.insert_one({
            "_id": ObjectId(self.id),
            "user_id": self.user_id,
            "amount": self.amount,
            "transaction_type": self.transaction_type.value,
            "description": self.description,
            "job_id": self.job_id,
            "created_at": self.created_at
        })

    @staticmethod
    async def get_by_user(user_id: str, limit: int = 100):
        db = get_db()
        transactions = []
        async for tx in db.credit_transactions.find(
            {"user_id": user_id}
        ).sort("created_at", -1).limit(limit):
            transactions.append({
                "id": str(tx["_id"]),
                "amount": tx["amount"],
                "transaction_type": tx["transaction_type"],
                "description": tx["description"],
                "job_id": tx.get("job_id"),
                "created_at": tx["created_at"]
            })
        return transactions

    @staticmethod
    async def get_balance(user_id: str) -> int:
        db = get_db()
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$group": {"_id": None, "total": {"$sum": "$amount"}}}
        ]
        result = await db.credit_transactions.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0