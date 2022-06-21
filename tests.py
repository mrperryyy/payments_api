from re import L
import pytest
import json
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from api import app
from config import Config


# TODO: figure out why fixure is not working. Client has no post/get functions?
# @pytest.fixture()
# def client():
#     with app.test_client() as client:
#         app.config.from_object(Config)
#         db = SQLAlchemy(app)
#         migrate = Migrate(app, db)
#         yield client


def test_create_loan():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        test_data = {'principal': 100}
        resp = client.post('/loan/create', json=test_data)
        status_code = resp.status_code
        resp = json.loads(resp.data)
        assert resp['principal'] == 100
        assert resp['balance'] == 100
        assert status_code == 201

def test_create_and_get_loan():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        test_data = {'principal': 200}
        resp_create = client.post('/loan/create', json=test_data)
        assert resp_create.status_code == 201

        resp_data = json.loads(resp_create.data)
        loan_id = resp_data['id']

        resp_get = client.get('/loan/'+str(loan_id))
        assert resp_get.status_code == 200
        
        get_data = json.loads(resp_get.data)
        assert get_data['id'] == loan_id
        assert get_data['principal'] == 200
        assert get_data['balance'] == 200

def test_create_loan_invalid_input():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        test_data = {'principal': 'Hello World'}
        resp = client.post('/loan/create', json=test_data)
        assert resp.status_code == 400

def test_create_negative_loan():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        test_data = {'principal': -100}
        resp = client.post('/loan/create', json=test_data)
        assert resp.status_code == 400

def test_get_nonexistent_loan():
    pass

def test_make_payment():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        loan_data = {'principal': 100}
        resp = client.post('/loan/create', json=loan_data)
        loan_data = json.loads(resp.data)
        
        payment_data = {'amount': 10, 'loan_id': loan_data['id']}
        resp = client.post('/payment/create', json=payment_data)
        payment_data = json.loads(resp.data)
        assert payment_data['amount'] == 10
        assert payment_data['loan_balance'] == 90

        resp = client.get('/loan/'+str(loan_data['id']))
        loan_data = json.loads(resp.data)
        assert loan_data['balance'] == 90

def test_make_negative_payment():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        loan_data = {'principal': 100}
        resp = client.post('/loan/create', json=loan_data)
        loan_data = json.loads(resp.data)

        payment_data = {'amount': -10, 'loan_id': loan_data['id']}
        resp = client.post('/payment/create', json=payment_data)
        assert resp.status_code == 400

def test_make_payment_too_large():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        loan_data = {'principal': 100}
        resp = client.post('/loan/create', json=loan_data)
        loan_data = json.loads(resp.data)

        payment_data = {'amount': 200, 'loan_id': loan_data['id']}
        resp = client.post('/payment/create', json=payment_data)
        assert resp.status_code == 400

def test_make_payment_nonexistent_loan():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        payment_data = {'amount': 10, 'loan_id': 100000}
        resp = client.post('/payment/create', json=payment_data)
        assert resp.status_code == 400

def test_refund_payment():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        loan_data = {'principal': 100}
        resp = client.post('/loan/create', json=loan_data)
        loan_data = json.loads(resp.data)

        payment_data = {'amount': 10, 'loan_id': loan_data['id']}
        resp = client.post('/payment/create', json=payment_data)
        payment_data = json.loads(resp.data)
        assert payment_data['loan_balance'] == 90

        refund_data = {'payment_id': payment_data['id']}
        resp = client.post('/payment/refund', json=refund_data)
        refund_data = json.loads(resp.data)
        assert refund_data['loan_balance'] == 100

        resp = client.get('/loan/'+str(loan_data['id']))
        loan_data = json.loads(resp.data)
        assert loan_data['balance'] == 100

        resp = client.get('/payment/'+str(payment_data['id']))
        payment_data = json.loads(resp.data)
        assert payment_data['status'] == 'Refunded'

def test_refund_nonexistent_payment():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        refund_data = {'payment_id': 10000000}
        resp = client.post('/payment/refund', json=refund_data)
        assert resp.status_code == 400

def test_refund_refunded_payment():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        loan_data = {'principal': 100}
        resp = client.post('/loan/create', json=loan_data)
        loan_data = json.loads(resp.data)

        payment_data = {'amount': 10, 'loan_id': loan_data['id']}
        resp = client.post('/payment/create', json=payment_data)
        payment_data = json.loads(resp.data)

        refund_data = {'payment_id': payment_data['id']}
        resp = client.post('/payment/refund', json=refund_data)
        refund_data = json.loads(resp.data)
        
        refund_data = {'payment_id': payment_data['id']}
        resp = client.post('/payment/refund', json=refund_data)        
        assert resp.status_code == 400

def test_close_loan():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        loan_data = {'principal': 100}
        resp = client.post('/loan/create', json=loan_data)
        loan_data = json.loads(resp.data)

        payment_data = {'amount': 100, 'loan_id': loan_data['id']}
        resp = client.post('/payment/create', json=payment_data)
        payment_data = json.loads(resp.data)

        close_loan_json = {'loan_id': loan_data['id']}
        resp = client.put('/loan/close', json=close_loan_json)
        assert resp.status_code == 200

        close_loan_data = json.loads(resp.data)
        assert close_loan_data['status'] == 'Closed'
        assert close_loan_data['balance'] == 0

def test_close_closed_loan():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        loan_data = {'principal': 100}
        resp = client.post('/loan/create', json=loan_data)
        loan_data = json.loads(resp.data)

        payment_data = {'amount': 100, 'loan_id': loan_data['id']}
        resp = client.post('/payment/create', json=payment_data)
        payment_data = json.loads(resp.data)

        close_loan_json = {'loan_id': loan_data['id']}
        resp = client.put('/loan/close', json=close_loan_json)
        assert resp.status_code == 200

        resp = client.put('/loan/close', json=close_loan_json)
        assert resp.status_code == 400

def test_close_loan_with_balance():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        loan_data = {'principal': 100}
        resp = client.post('/loan/create', json=loan_data)
        loan_data = json.loads(resp.data)

        payment_data = {'amount': 10, 'loan_id': loan_data['id']}
        resp = client.post('/payment/create', json=payment_data)
        payment_data = json.loads(resp.data)

        close_loan_json = {'loan_id': loan_data['id']}
        resp = client.put('/loan/close', json=close_loan_json)
        assert resp.status_code == 400

def test_make_payment_to_closed_loan():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        loan_data = {'principal': 100}
        resp = client.post('/loan/create', json=loan_data)
        loan_data = json.loads(resp.data)

        payment_data = {'amount': 100, 'loan_id': loan_data['id']}
        resp = client.post('/payment/create', json=payment_data)
        payment_data = json.loads(resp.data)

        close_loan_json = {'loan_id': loan_data['id']}
        resp = client.put('/loan/close', json=close_loan_json)
        assert resp.status_code == 200

        resp = client.post('/payment/create', json=payment_data)
        assert resp.status_code == 400

def test_refund_closed_loan():
    with app.test_client() as client:
        app.config.from_object(Config)
        db = SQLAlchemy(app)
        migrate = Migrate(app, db)

        loan_data = {'principal': 100}
        resp = client.post('/loan/create', json=loan_data)
        loan_data = json.loads(resp.data)

        payment_data = {'amount': 100, 'loan_id': loan_data['id']}
        resp = client.post('/payment/create', json=payment_data)
        payment_data = json.loads(resp.data)

        close_loan_json = {'loan_id': loan_data['id']}
        resp = client.put('/loan/close', json=close_loan_json)
        assert resp.status_code == 200

        refund_json = {'payment_id': payment_data['id']}
        resp = client.post('/payment/refund', json=refund_json)
        assert resp.status_code == 400
