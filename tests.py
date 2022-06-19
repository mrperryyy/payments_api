import pytest
import json
import requests
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from api import app
from config import Config


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