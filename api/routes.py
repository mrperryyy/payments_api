from datetime import datetime
from flask import request, make_response, jsonify, url_for, abort
from pydantic import ValidationError

from api import app, db
from api.models import User, Loan, Payment
from api.validators import UserValidator, LoanValidator, CloseLoanValidator, PaymentValidator, RefundValidator
from api.auth import basic_auth

@app.route('/user/create', methods=['POST'])
def create_user():
    '''
    Creates a user
    '''
    json_data = request.get_json(force=True)

    try:
        # validate request
        user_data = UserValidator(**json_data)

        user = User(username=user_data.username)
        user.set_password(user_data.password)
        db.session.add(user)
        db.session.commit()

        response = make_response(jsonify(user.to_dict()), 201)
        response.headers['Location'] = url_for('get_loan', id=user.id)
        return response
    
    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)

@app.route('/user/<int:id>', methods=['GET'])
def get_user(id):
    return jsonify(User.query.get_or_404(id).to_dict())

@app.route('/loan/create', methods=['POST'])
@basic_auth.login_required
def create_loan():
    '''
    Creates a loan from JSON request.
    '''
    json_data = request.get_json(force=True)

    try:
        # validate request
        loan_data = LoanValidator(**json_data)

        # create loan
        loan = Loan(principal=loan_data.principal, balance=loan_data.principal, user=basic_auth.current_user())
        db.session.add(loan)
        db.session.commit()

        # create 201 reponse
        response = make_response(jsonify(loan.to_dict()), 201)
        response.headers['Location'] = url_for('get_loan', id=loan.id)
        return response

    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)

@app.route('/loan/close', methods=['PUT'])
@basic_auth.login_required
def close_loan():
    '''
    Closes loan with 0 balance.
    '''
    json_data = request.get_json(force=True)

    try:
        # validate request
        loan_data = CloseLoanValidator(**json_data)

        loan = Loan.query.get(loan_data.loan_id)
        if loan.user_id != basic_auth.current_user().id:
            abort(403)
        
        loan.status = 'Closed'
        db.session.commit()

        payload = loan.to_dict()
        response = make_response(payload, 200)
        return response

    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)

@app.route('/loan/<int:id>', methods=['GET'])
def get_loan(id):
    return jsonify(Loan.query.get_or_404(id).to_dict())

@app.route('/payment/create', methods=['POST'])
@basic_auth.login_required
def make_payment():
    '''
    Create payment from JSON request.
    '''
    json_data = request.get_json(force=True)

    try:
        # validate json data
        payment_data = PaymentValidator(**json_data)

        # create payment and update loan balance
        loan = Loan.query.get(payment_data.loan_id)
        if loan.user_id != basic_auth.current_user().id:
            abort(403)
        
        payment = Payment(amount=payment_data.amount, loan=loan)
        loan.balance = loan.balance - payment.amount
        loan.time_last_payment = datetime.now()
        db.session.add(payment)
        db.session.commit()
        
        # create 201 response, add loan balance to payload
        payload = payment.to_dict()
        payload['loan_balance'] = loan.balance
        response = make_response(jsonify(payload), 201)
        response.headers['Location'] = url_for('get_payment', id=payment.id)
        return response
    
    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)

@app.route('/payment/<int:id>', methods=['GET'])
def get_payment(id):
    '''
    Retrieve payment
    '''
    return jsonify(Payment.query.get_or_404(id).to_dict())

@app.route('/payment/refund', methods=['PUT'])
@basic_auth.login_required
def refund_payment():
    '''
    Refund previous payment
    '''
    json_data = request.get_json(force=True)

    try:
        refund_data = RefundValidator(**json_data)

        payment = Payment.query.get(refund_data.payment_id)
        loan = Loan.query.get(payment.loan_id)
        if loan.user_id != basic_auth.current_user().id:
            abort(403)
        
        payment.status = 'Refunded'
        loan.balance = loan.balance + payment.amount
        db.session.commit()

        payload = payment.to_dict()
        payload['loan_balance'] = loan.balance
        response = make_response(payload, 200)
        return response
    
    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)