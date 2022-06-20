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

    def to_dict(self):
        return {
            'id': self.id,
            'principal': self.principal,
            'balance': self.balance,
        }

class LoanValidator(BaseModel):
    principal: float

    @validator('principal')
    def principal_must_be_positive(cls, principal):
        if principal <= 0:
            raise ValueError(f"Loan principal must be greater than 0.")
        #TODO: return principal??

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float)
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'loan_id': self.loan_id
        }

class PaymentValidator(BaseModel):
    loan_id: int
    amount: float

    @validator('loan_id')
    def loan_must_exist(cls, loan_id):
        if db.session.query(Loan.id).filter_by(id=loan_id).first() is None:
            raise ValueError(f"Error! loan_id: {loan_id} does not exist.")
        return loan_id
    
    @validator('amount')
    def amount_must_be_positive(cls, amount):
        if amount <= 0:
            raise ValueError(f"Payment amount must be greater than 0.")
        return amount
    
    @validator('amount')
    def amount_less_than_balance(cls, amount, values):
        if 'loan_id' in values:
            loan_id = values['loan_id']
            loan = db.session.query(Loan).filter_by(id=loan_id).first()
            
            if loan.balance < amount:
                raise ValueError(f"Payment cannot be greater than loan balance. Current balance: {loan.balance}.")
            return amount
