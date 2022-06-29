from datetime import datetime
from api.db.orm import Loan
from api.db.crud import find_user

def check_resource_exists(resource) -> None:
    if resource is None:
        raise ValueError(f"Resource not found.")

def check_username_unique(username: str) -> None:
    if find_user(username) is not None:
        raise ValueError(f"Username {username} is already in use.")

def check_loan_empty_balance(loan: Loan) -> None:
    if loan.balance > 0:
        raise ValueError(f"Loan {loan.id} balance is not zero. Current balance: {loan.balance}")

def check_loan_open(loan: Loan) -> None:
    if loan.status != 'Open':
        raise ValueError(f"Loan {loan.id} is closed. No more payments or refunds can be processed.")

# TODO: idempotency
def check_duplicate_payment(loan: Loan) -> None:
    if loan and loan.time_last_payment is not None:
        current_time = datetime.now()
        if (current_time - loan.time_last_payment).seconds < 10:
            raise ValueError(f"A payment was made to loan {loan.id} in the past 10 seconds. Please wait before making another payment.")

def check_payment_less_than_balance(loan: Loan, payment_amount: float):
    if loan.balance < payment_amount:
        raise ValueError(f"Payment cannot be greater than loan balance. Current balance: {loan.balance}.")

def check_payment_complete(payment):
    if payment.status == 'Refunded':
        raise ValueError(f"Payment has already been refunded.")
