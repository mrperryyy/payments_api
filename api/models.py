import base64
import os
from datetime import datetime, timedelta
from flask import jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from api import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    loans = db.relationship('Loan', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'username': self.username
        }
    
    # def get_token(self, expires_in=3600):
    #     now = datetime.utcnow()
    #     if self.token and self.token_expiration > now + timedelta(seconds=60):
    #         return self.token
        
    #     self.token = base64.b64encode(os.urandom(24)).decode('utf-8')
    #     self.token_expiration = now + timedelta(seconds=expires_in)
    #     db.session.add(self)
    #     return self.token
    
    # def revoke_token(self):
    #     self.token_expiration = datetime.utcnow() - timedelta(seconds=1)
    
    # @staticmethod
    # def check_token(token):
    #     user = User.query.filter_by(token=token).first()
    #     if user is None or user.token_expiration < datetime.utcnow():
    #         return None
    #     return user

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), default=datetime.now())
    time_last_payment = db.Column(db.DateTime(timezone=True), default=None)
    principal = db.Column(db.Float)
    balance = db.Column(db.Float)
    status = db.Column(db.String(6), default='Open')
    payments = db.relationship('Payment', backref='loan', lazy='dynamic')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

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
