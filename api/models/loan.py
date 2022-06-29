from pydantic import BaseModel, validator
from api.db.orm import db, Loan

class LoanModel(BaseModel):
    principal: float

    @validator('principal')
    def principal_must_be_positive(cls, principal):
        if principal <= 0:
            raise ValueError(f"Loan principal must be greater than 0.")
        return principal

class CloseLoanModel(BaseModel):
    loan_id: int
