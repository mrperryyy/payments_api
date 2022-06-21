from pydantic import BaseModel, ValidationError, validator, confloat
from api import db
from api.models import Loan, Payment

class LoanValidator(BaseModel):
    principal: float

    @validator('principal')
    def principal_must_be_positive(cls, principal):
        if principal <= 0:
            raise ValueError(f"Loan principal must be greater than 0.")
        return principal

class PaymentValidator(BaseModel):
    loan_id: int
    amount: float

    @validator('loan_id')
    def loan_must_exist(cls, loan_id):
        if db.session.query(Loan.id).filter_by(id=loan_id).first() is None:
            raise ValueError(f"loan_id: {loan_id} does not exist.")
        return loan_id
    
    @validator('amount')
    def amount_must_be_positive(cls, amount):
        if amount <= 0:
            raise ValueError(f"Payment amount must be greater than 0.")
        return amount
    
    @validator('amount')
    def amount_less_than_balance(cls, amount, values):
        if 'loan_id' in values:
            loan_id = values['loan_id']
            loan = db.session.query(Loan).filter_by(id=loan_id).first()
            
            if loan.balance < amount:
                raise ValueError(f"Payment cannot be greater than loan balance. Current balance: {loan.balance}.")
            return amount

class RefundValidator(BaseModel):
    payment_id: int

    @validator('payment_id')
    def payment_must_exist(cls, payment_id):
        if db.session.query(Payment.id).filter_by(id=payment_id).first() is None:
            raise ValueError(f"payment_id: {payment_id} does not exist.")
        return payment_id
    
    @validator('payment_id')
    def payment_must_be_complete(cls, payment_id):
        payment = db.session.query(Payment).filter_by(id=payment_id).first()
        if payment is not None and payment.status == 'Refunded':
            raise ValueError(f"Payment has already been refunded.")
        return payment_id
