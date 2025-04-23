from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class TransactionType(str, Enum):
    JOB_APPLICATION = "job_application"
    TOPUP = "topup"

class CreditPackage(str, Enum):
    REGULAR = "regular"
    PLUS = "plus"
    PRO = "pro"

class CreditTopupRequest(BaseModel):
    package: CreditPackage
    payment_method: str

class CreditTransactionOut(BaseModel):
    id: str
    amount: int
    transaction_type: TransactionType
    description: str
    created_at: datetime