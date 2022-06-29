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

    @validator('loan_id')
    def loan_must_exist(cls, loan_id):
        if db.session.query(Loan.id).filter_by(id=loan_id).first() is None:
            raise ValueError(f"loan_id: {loan_id} does not exist.")
        return loan_id

    @validator('loan_id')
    def loan_must_have_zero_balance(cls, loan_id):
        loan = db.session.query(Loan).filter_by(id=loan_id).first()
        if loan and loan.balance > 0:
            raise ValueError(f"loan_id: {loan_id} balance is not zero. Current balance: {loan.balance}")
        return loan_id
    
    @validator('loan_id')
    def loan_must_be_open(cls, loan_id):
        loan = db.session.query(Loan).filter_by(id=loan_id).first()
        if loan and loan.status == 'Closed':
            raise ValueError(f"loan_id: {loan_id} is already closed.")
        return loan_id
