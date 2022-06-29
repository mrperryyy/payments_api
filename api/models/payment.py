from datetime import datetime
from pydantic import BaseModel, validator
from api.db.orm import db, Loan, Payment

class PaymentModel(BaseModel):
    loan_id: int
    amount: float

    @validator('loan_id')
    def loan_must_exist(cls, loan_id):
        if db.session.query(Loan.id).filter_by(id=loan_id).first() is None:
            raise ValueError(f"loan_id: {loan_id} does not exist.")
        return loan_id
    
    @validator('loan_id')
    def check_duplicate_payment(cls, loan_id):
        loan = db.session.query(Loan).filter_by(id=loan_id).first()
        if loan and loan.time_last_payment is not None:
            current_time = datetime.now()
            if (current_time - loan.time_last_payment).seconds < 10:
                raise ValueError(f"A payment was made to loan {loan_id} in the past 10 seconds. Please wait before making another payment.")
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
            
            if loan and loan.balance < amount:
                raise ValueError(f"Payment cannot be greater than loan balance. Current balance: {loan.balance}.")
            return amount

class RefundModel(BaseModel):
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
    
    @validator('payment_id')
    def loan_must_be_open(cls, payment_id):
        payment = db.session.query(Payment).filter_by(id=payment_id).first()
        loan = db.session.query(Loan).filter_by(id=payment.loan_id).first()
        if loan.status == 'Closed':
            raise ValueError(f"loan_id: {payment.loan_id} is closed. Its payments cannot be refunded.")
        return payment_id
