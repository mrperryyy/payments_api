from api.db.orm import db
from api.db.orm import User, Loan

def add_user(user: User) -> None:
    db.session.add(user)
    db.session.commit()

def create_loan(loan: Loan) -> None:
    db.session.add(loan)
    db.session.commit()