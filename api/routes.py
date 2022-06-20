from flask import request, make_response, jsonify, url_for
from pydantic import ValidationError

from api import app, db
from api.models import Loan, LoanValidator, Payment, PaymentValidator
from api.errors import bad_request

@app.route('/index')
def index():
    return "Hello, World!"


@app.route('/loan/create', methods=['POST'])
def create_loan():
    '''
    Creates a loan from JSON request.
    '''
    data = request.get_json(force=True)

    try:
        LoanValidator(**data)

        loan = Loan(principal=data['principal'], balance=data['principal'])
        db.session.add(loan)
        db.session.commit()

        # create 201 reponse
        response = jsonify(loan.to_dict())
        response.status_code = 201
        response.headers['Location'] = url_for('get_loan', id=loan.id)
        return response

    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)


@app.route('/loan/<int:id>', methods=['GET'])
def get_loan(id):
    return jsonify(Loan.query.get_or_404(id).to_dict())

@app.route('/payment/create', methods=['POST'])
def make_payment():
    '''
    Create payment from JSON request.
    '''
    json_data = request.get_json(force=True)

    try:
        payment_data = PaymentValidator(**json_data)

        loan = Loan.query.get(payment_data.loan_id)
        payment = Payment(amount=payment_data.amount, loan=loan)
        loan.balance = loan.balance - payment.amount
        db.session.add(payment)
        db.session.commit()
        
        response = payment.to_dict()
        response['loan_balance'] = loan.balance
        response = jsonify(response)
        response.status_code = 201
        response.headers['Location'] = url_for('get_payment', id=payment.id)
        return response
    
    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)

@app.route('/payment/<int:id>', methods=['GET'])
def get_payment():
    '''
    Retrieve payment
    '''
    return jsonify(Payment.query.get_or_404(id).to_dict())
