import pytest
from datetime import datetime
from unittest.mock import patch
from api.db.orm import User, Loan, Payment

@patch('api.routes.payment.find_loan', return_value=Loan(user_id=1, principal=100, balance=100, status='Open'))
@patch('api.routes.payment.basic_auth.current_user', return_value=User(id=1))
@patch('api.routes.helpers.find_recent_loan_payment', return_value=None)
@patch('api.routes.payment.add_payment')
@patch('api.routes.payment.url_for', return_value=None)
def test_make_payment(find_loan, curr_user, recent_payment, add_payment, url, client):
    payment_input = {'loan_id': 1, 'amount': 10}
    response = client.post('/payment', json=payment_input)
    assert response.status_code == 201

@pytest.mark.parametrize('input', ['Hello', -100])
@patch('api.routes.payment.find_loan', return_value=Loan(user_id=1, principal=100, balance=100, status='Open'))
@patch('api.routes.payment.basic_auth.current_user', return_value=User(id=1))
@patch('api.routes.helpers.find_recent_loan_payment', return_value=None)
def test_make_payment_invalid_input(find_loan, curr_user, recent_payment, input, client):
    payment_input = {'loan_id': 1, 'amount': input}
    response = client.post('/payment', json=payment_input)
    assert response.status_code == 400

@patch('api.routes.payment.find_loan', return_value=None)
@patch('api.routes.payment.basic_auth.current_user', return_value=User(id=1))
@patch('api.routes.helpers.find_recent_loan_payment', return_value=None)
def test_payment_nonexistent_loan(find_loan, curr_user, recent_payment, client):
    payment_input = {'loan_id': 1, 'amount': 10}
    response = client.post('/payment', json=payment_input)
    assert response.status_code == 400

@patch('api.routes.payment.find_loan', return_value=Loan(user_id=2, principal=100, balance=100, status='Open'))
@patch('api.routes.payment.basic_auth.current_user', return_value=User(id=1))
@patch('api.routes.helpers.find_recent_loan_payment', return_value=None)
def test_make_payment_wrong_user(find_loan, curr_user, recent_payment, client):
    payment_input = {'loan_id': 1, 'amount': 10}
    response = client.post('/payment', json=payment_input)
    assert response.status_code == 403

@patch('api.routes.payment.find_loan', return_value=Loan(user_id=1, principal=100, balance=100, status='Open'))
@patch('api.routes.payment.basic_auth.current_user', return_value=User(id=1))
@patch('api.routes.helpers.find_recent_loan_payment', return_value=Payment(time_created=datetime.utcnow()))
def test_duplicate_payment(find_loan, curr_user, recent_payment, client):
    payment_input = {'loan_id': 1, 'amount': 10}
    response = client.post('/payment', json=payment_input)
    assert response.status_code == 400

@patch('api.routes.payment.find_loan', return_value=Loan(user_id=1, principal=100, balance=100, status='Open'))
@patch('api.routes.payment.basic_auth.current_user', return_value=User(id=1))
@patch('api.routes.helpers.find_recent_loan_payment', return_value=None)
def test_payment_more_than_balance(find_loan, curr_user, recent_payment, client):
    payment_input = {'loan_id': 1, 'amount': 101}
    response = client.post('/payment', json=payment_input)
    assert response.status_code == 400

@patch('api.routes.payment.find_loan', return_value=Loan(user_id=1, principal=100, balance=0, status='Closed'))
@patch('api.routes.payment.basic_auth.current_user', return_value=User(id=1))
@patch('api.routes.helpers.find_recent_loan_payment', return_value=None)
def test_payment_closed_loan(find_loan, curr_user, recent_payment, client):
    payment_input = {'loan_id': 1, 'amount': 10}
    response = client.post('/payment', json=payment_input)
    assert response.status_code == 400

@patch('api.routes.payment.find_payment', return_value=Payment(loan_id=1, amount=10, status='Complete'))
@patch('api.routes.payment.find_loan', return_value=Loan(user_id=1, principal=100, balance=90, status='Open'))
@patch('api.routes.payment.basic_auth.current_user', return_value=User(id=1))
@patch('api.routes.payment.update_payment_status')
def test_refund_payment(find_payment, find_loan, user, status, client):
    refund_input = {'payment_id': 1}
    resp = client.put('/payment/refund', json=refund_input)
    assert resp.status_code == 200

@patch('api.routes.payment.find_payment', return_value=None)
@patch('api.routes.payment.find_loan', return_value=Loan(user_id=1, principal=100, balance=90, status='Open'))
@patch('api.routes.payment.basic_auth.current_user', return_value=User(id=1))
@patch('api.routes.payment.update_payment_status')
def test_refund_nonexistent_payment(find_payment, find_loan, user, status, client):
    refund_input = {'payment_id': 1}
    resp = client.put('/payment/refund', json=refund_input)
    assert resp.status_code == 400

@patch('api.routes.payment.find_payment', return_value=Payment(loan_id=1, amount=10, status='Complete'))
@patch('api.routes.payment.find_loan', return_value=Loan(user_id=2, principal=100, balance=90, status='Open'))
@patch('api.routes.payment.basic_auth.current_user', return_value=User(id=1))
@patch('api.routes.payment.update_payment_status')
def test_refund_wrong_user(find_payment, find_loan, user, status, client):
    refund_input = {'payment_id': 1}
    resp = client.put('/payment/refund', json=refund_input)
    assert resp.status_code == 403

@patch('api.routes.payment.find_payment', return_value=Payment(loan_id=1, amount=10, status='Refunded'))
@patch('api.routes.payment.find_loan', return_value=Loan(user_id=1, principal=100, balance=90, status='Open'))
@patch('api.routes.payment.basic_auth.current_user', return_value=User(id=1))
@patch('api.routes.payment.update_payment_status')
def test_refund_refunded_payment(find_payment, find_loan, user, status, client):
    refund_input = {'payment_id': 1}
    resp = client.put('/payment/refund', json=refund_input)
    assert resp.status_code == 400

@patch('api.routes.payment.find_payment', return_value=Payment(loan_id=1, amount=10, status='Complete'))
@patch('api.routes.payment.find_loan', return_value=Loan(user_id=1, principal=100, balance=0, status='Closed'))
@patch('api.routes.payment.basic_auth.current_user', return_value=User(id=1))
@patch('api.routes.payment.update_payment_status')
def test_refund_closed_loan(find_payment, find_loan, user, status, client):
    refund_input = {'payment_id': 1}
    resp = client.put('/payment/refund', json=refund_input)
    assert resp.status_code == 400
