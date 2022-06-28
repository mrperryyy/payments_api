import pytest
import json
import base64
import requests
# import requests_mock
from unittest.mock import patch
import time
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from api import app as application
from api.config import Config
# import api.db

@pytest.fixture()
def client():
    with application.test_client() as client:
        application.config.from_object(Config)
        db = SQLAlchemy(application)
        migrate = Migrate(application, db)
        yield client

def get_credential_header():
    credentials = base64.b64encode(b"mperry:password").decode('utf-8')
    return {'Authorization': f'Basic {credentials}'}

# def test_create_user(client):
#     user_data = {'username': 'user1', 'password': 'password'}
#     resp = client.post('/user/create', json=user_data)
#     assert resp.status_code == 201
    
#     user_resp = json.loads(resp.data)
#     assert user_resp['username'] == 'user1'

def test_create_loan(client):
    test_data = {'principal': 100}
    resp = client.post('/loan/create', json=test_data, headers=get_credential_header())
    status_code = resp.status_code
    resp = json.loads(resp.data)
    assert status_code == 201
    assert resp['principal'] == 100
    assert resp['balance'] == 100

def test_create_and_get_loan(client):
    test_data = {'principal': 200}
    resp_create = client.post('/loan/create', json=test_data, headers=get_credential_header())
    assert resp_create.status_code == 201

    resp_data = json.loads(resp_create.data)
    loan_id = resp_data['id']

    resp_get = client.get('/loan/'+str(loan_id))
    assert resp_get.status_code == 200
        
    get_data = json.loads(resp_get.data)
    assert get_data['id'] == loan_id
    assert get_data['principal'] == 200
    assert get_data['balance'] == 200

def test_create_loan_invalid_input(client):
    test_data = {'principal': 'Hello World'}
    resp = client.post('/loan/create', json=test_data, headers=get_credential_header())
    assert resp.status_code == 400

def test_create_negative_loan(client):
    test_data = {'principal': -100}
    resp = client.post('/loan/create', json=test_data, headers=get_credential_header())
    assert resp.status_code == 400

def test_get_nonexistent_loan():
    pass

def test_make_payment(client):
    loan_data = {'principal': 100}
    resp = client.post('/loan/create', json=loan_data, headers=get_credential_header())
    loan_data = json.loads(resp.data)
        
    payment_data = {'amount': 10, 'loan_id': loan_data['id']}
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    payment_data = json.loads(resp.data)
    assert payment_data['amount'] == 10
    assert payment_data['loan_balance'] == 90

    resp = client.get('/loan/'+str(loan_data['id']))
    loan_data = json.loads(resp.data)
    assert loan_data['balance'] == 90

def test_make_negative_payment(client):
    loan_data = {'principal': 100}
    resp = client.post('/loan/create', json=loan_data, headers=get_credential_header())
    loan_data = json.loads(resp.data)

    payment_data = {'amount': -10, 'loan_id': loan_data['id']}
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    assert resp.status_code == 400

def test_make_payment_too_large(client):
    loan_data = {'principal': 100}
    resp = client.post('/loan/create', json=loan_data, headers=get_credential_header())
    loan_data = json.loads(resp.data)

    payment_data = {'amount': 200, 'loan_id': loan_data['id']}
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    assert resp.status_code == 400

def test_make_payment_nonexistent_loan(client):
    payment_data = {'amount': 10, 'loan_id': 100000}
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    assert resp.status_code == 400

def test_make_duplicate_payment(client):
    loan_data = {'principal': 100}
    resp = client.post('/loan/create', json=loan_data, headers=get_credential_header())
    loan_data = json.loads(resp.data)

    payment_data = {'amount': 100, 'loan_id': loan_data['id']}
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    assert resp.status_code == 201
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    assert resp.status_code == 400

def test_refund_payment(client):
    loan_data = {'principal': 100}
    resp = client.post('/loan/create', json=loan_data, headers=get_credential_header())
    loan_data = json.loads(resp.data)

    payment_data = {'amount': 10, 'loan_id': loan_data['id']}
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    payment_data = json.loads(resp.data)
    assert payment_data['loan_balance'] == 90

    refund_data = {'payment_id': payment_data['id']}
    resp = client.put('/payment/refund', json=refund_data, headers=get_credential_header())
    refund_data = json.loads(resp.data)
    assert refund_data['loan_balance'] == 100

    resp = client.get('/loan/'+str(loan_data['id']))
    loan_data = json.loads(resp.data)
    assert loan_data['balance'] == 100

    resp = client.get('/payment/'+str(payment_data['id']))
    payment_data = json.loads(resp.data)
    assert payment_data['status'] == 'Refunded'

def test_refund_nonexistent_payment(client):
    refund_data = {'payment_id': 10000000}
    resp = client.put('/payment/refund', json=refund_data, headers=get_credential_header())
    assert resp.status_code == 400

def test_refund_refunded_payment(client):
    loan_data = {'principal': 100}
    resp = client.post('/loan/create', json=loan_data, headers=get_credential_header())
    loan_data = json.loads(resp.data)

    payment_data = {'amount': 10, 'loan_id': loan_data['id']}
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    payment_data = json.loads(resp.data)

    refund_data = {'payment_id': payment_data['id']}
    resp = client.put('/payment/refund', json=refund_data, headers=get_credential_header())
    refund_data = json.loads(resp.data)
        
    refund_data = {'payment_id': payment_data['id']}
    resp = client.put('/payment/refund', json=refund_data, headers=get_credential_header())        
    assert resp.status_code == 400

def test_close_loan(client):
    loan_data = {'principal': 100}
    resp = client.post('/loan/create', json=loan_data, headers=get_credential_header())
    loan_data = json.loads(resp.data)

    payment_data = {'amount': 100, 'loan_id': loan_data['id']}
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    payment_data = json.loads(resp.data)

    close_loan_json = {'loan_id': loan_data['id']}
    resp = client.put('/loan/close', json=close_loan_json, headers=get_credential_header())
    assert resp.status_code == 200

    close_loan_data = json.loads(resp.data)
    assert close_loan_data['status'] == 'Closed'
    assert close_loan_data['balance'] == 0

def test_close_closed_loan(client):
    loan_data = {'principal': 100}
    resp = client.post('/loan/create', json=loan_data, headers=get_credential_header())
    loan_data = json.loads(resp.data)

    payment_data = {'amount': 100, 'loan_id': loan_data['id']}
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    payment_data = json.loads(resp.data)

    close_loan_json = {'loan_id': loan_data['id']}
    resp = client.put('/loan/close', json=close_loan_json, headers=get_credential_header())
    assert resp.status_code == 200

    resp = client.put('/loan/close', json=close_loan_json, headers=get_credential_header())
    assert resp.status_code == 400

def test_close_loan_with_balance(client):
    loan_data = {'principal': 100}
    resp = client.post('/loan/create', json=loan_data, headers=get_credential_header())
    loan_data = json.loads(resp.data)

    payment_data = {'amount': 10, 'loan_id': loan_data['id']}
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    payment_data = json.loads(resp.data)

    close_loan_json = {'loan_id': loan_data['id']}
    resp = client.put('/loan/close', json=close_loan_json, headers=get_credential_header())
    assert resp.status_code == 400

def test_make_payment_to_closed_loan(client):
    loan_data = {'principal': 100}
    resp = client.post('/loan/create', json=loan_data, headers=get_credential_header())
    loan_data = json.loads(resp.data)

    payment_data = {'amount': 100, 'loan_id': loan_data['id']}
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    payment_data = json.loads(resp.data)

    close_loan_json = {'loan_id': loan_data['id']}
    resp = client.put('/loan/close', json=close_loan_json, headers=get_credential_header())
    assert resp.status_code == 200

    time.sleep(11)
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    assert resp.status_code == 400

def test_refund_closed_loan(client):
    loan_data = {'principal': 100}
    resp = client.post('/loan/create', json=loan_data, headers=get_credential_header())
    loan_data = json.loads(resp.data)

    payment_data = {'amount': 100, 'loan_id': loan_data['id']}
    resp = client.post('/payment/create', json=payment_data, headers=get_credential_header())
    payment_data = json.loads(resp.data)

    close_loan_json = {'loan_id': loan_data['id']}
    resp = client.put('/loan/close', json=close_loan_json, headers=get_credential_header())
    assert resp.status_code == 200

    refund_json = {'payment_id': payment_data['id']}
    resp = client.put('/payment/refund', json=refund_json, headers=get_credential_header())
    assert resp.status_code == 400
