import pytest
from unittest.mock import patch
from api.db.orm import User, Loan

@patch('api.routes.loan.add_loan')
@patch('api.routes.loan.url_for', return_value=None)
def test_create_loan(add_loan, url_for, client):
    loan_input = {'principal': 100}
    response = client.post('/loan', json=loan_input)
    assert response.status_code == 201
    assert response.json['principal'] == 100
    assert response.json['balance'] == 100

@pytest.mark.parametrize('input', ['Hello', -100])
def test_create_loan_invalid_input(input, client):
    loan_input = {'principal': input}
    resp = client.post('/loan', json=loan_input)
    assert resp.status_code == 400

@patch('api.routes.loan.find_loan', return_value=Loan(user_id=1, principal=100, balance=0, status='Open'))
@patch('api.routes.loan.basic_auth.current_user', return_value=User(id=1))
def test_close_loan(find_loan, current_user, client):
    close_loan_input = {'loan_id': 1}
    resp = client.put('/loan/close', json=close_loan_input)
    assert resp.status_code == 200

@patch('api.routes.loan.find_loan', return_value=Loan(user_id=1, principal=100, balance=0, status='Open'))
@patch('api.routes.loan.basic_auth.current_user', return_value=User(id=1))
def test_close_loan_invalid_input(find_loan, current_user, client):
    close_loan_input = {'loan_id': 'one'}
    resp = client.put('/loan/close', json=close_loan_input)
    assert resp.status_code == 400

@patch('api.routes.loan.find_loan', return_value=Loan(user_id=1, principal=100, balance=0, status='Closed'))
@patch('api.routes.loan.basic_auth.current_user', return_value=User(id=1))
def test_close_loan_already_closed(find_loan, current_user, client):
    close_loan_input = {'loan_id': 1}
    resp = client.put('/loan/close', json=close_loan_input)
    assert resp.status_code == 400

@patch('api.routes.loan.find_loan', return_value=Loan(user_id=1, principal=100, balance=0, status='Open'))
@patch('api.routes.loan.basic_auth.current_user', return_value=User(id=2))
def test_close_loan_wrong_user(find_loan, current_user, client):
    close_loan_input = {'loan_id': 1}
    resp = client.put('/loan/close', json=close_loan_input)
    assert resp.status_code == 403

@patch('api.routes.loan.find_loan', return_value=None)
@patch('api.routes.loan.basic_auth.current_user', return_value=User(id=1))
def test_close_nonexistent_loan(find_loan, current_user, client):
    close_loan_input = {'loan_id': 1}
    resp = client.put('/loan/close', json=close_loan_input)
    assert resp.status_code == 400

@patch('api.routes.loan.find_loan', return_value=Loan(user_id=1, principal=100, balance=10, status='Open'))
@patch('api.routes.loan.basic_auth.current_user', return_value=User(id=1))
def test_close_loan_balance(find_loan, current_user, client):
    close_loan_input = {'loan_id': 1}
    resp = client.put('/loan/close', json=close_loan_input)
    assert resp.status_code == 400
