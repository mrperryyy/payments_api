from datetime import datetime
from pydantic import BaseModel, validator
from api.db.orm import db, Loan, Payment

class PaymentModel(BaseModel):
    loan_id: int
    amount: float

    @validator('amount')
    def amount_must_be_positive(cls, amount):
        if amount <= 0:
            raise ValueError(f"Payment amount must be greater than 0.")
        return amount

class RefundModel(BaseModel):
    payment_id: int
