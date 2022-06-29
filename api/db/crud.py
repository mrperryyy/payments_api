from typing import Optional
from api.db.orm import db
from api.db.orm import User, Loan, Payment

def add_user(user: User) -> None:
    db.session.add(user)
    db.session.commit()

def find_user(username: str) -> Optional[User]:
    return db.session.query(User).filter_by(username=username).first()

def add_loan(loan: Loan) -> None:
    db.session.add(loan)
    db.session.commit()

def find_loan(loan_id: int) -> Optional[Loan]:
    return Loan.query.get(loan_id)

def update_loan_status(loan: Loan, status: str) -> None:
    loan.status = status
    db.session.commit()

def add_payment(payment: Payment, loan: Loan) -> None:
    loan.balance = loan.balance - payment.amount
    db.session.add(payment)
    db.session.commit()

def find_payment(payment_id: int) -> Optional[Payment]:
    return Payment.query.get(payment_id)

def update_payment_status(payment: Payment, status: str, loan=None) -> None:
    payment.status = status
    if loan:
        loan.balance = loan.balance + payment.amount
    db.session.commit()

def find_recent_loan_payment(loan: Loan, amount: float) -> Optional[Payment]:
    return db.session.query(Payment).filter_by(loan_id=loan.id, amount=amount).order_by(Payment.time_created.desc()).first()
