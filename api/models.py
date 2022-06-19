from datetime import datetime
from flask import jsonify
from pydantic import BaseModel, ValidationError, validator, confloat
from api import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}'.format(self.username)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    principal = db.Column(db.Float)
    balance = db.Column(db.Float)
    payments = db.relationship('Payment', backref='loan', lazy='dynamic')

    def to_json(self):
        return jsonify({
            'id': self.id,
            'principal': self.principal,
            'balance': self.balance,
        })

class LoanValidator(BaseModel):
    principal: confloat(ge=0)

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))
