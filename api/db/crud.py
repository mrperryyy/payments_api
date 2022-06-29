from api.db.orm import db
from api.db.orm import User, Loan, Payment

def add_user(user: User) -> None:
    db.session.add(user)
    db.session.commit()

def add_loan(loan: Loan) -> None:
    db.session.add(loan)
    db.session.commit()

def update_loan_status(loan: Loan, status: str) -> None:
    loan.status = status
    db.session.commit()

def add_payment(payment: Payment, loan: Loan) -> None:
    loan.balance = loan.balance - payment.amount
    db.session.add(payment)
    db.session.commit()