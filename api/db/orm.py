
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

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

class Loan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
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
    time_created = db.Column(db.DateTime(timezone=True), default=datetime.utcnow)
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
