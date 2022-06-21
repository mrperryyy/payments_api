from datetime import datetime
from flask import jsonify
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
    time_created = db.Column(db.DateTime(timezone=True), default=datetime.now())
    time_last_payment = db.Column(db.DateTime(timezone=True), default=None)
    principal = db.Column(db.Float)
    balance = db.Column(db.Float)
    status = db.Column(db.String(6), default='Open')
    payments = db.relationship('Payment', backref='loan', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'principal': self.principal,
            'balance': self.balance,
            'status': self.status
        }

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), default=datetime.now())
    amount = db.Column(db.Float)
    status = db.Column(db.String(8), default='Complete')
    loan_id = db.Column(db.Integer, db.ForeignKey('loan.id'))

    def to_dict(self):
        return {
            'id': self.id,
            'amount': self.amount,
            'status': self.status,
            'loan_id': self.loan_id
        }
