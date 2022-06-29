from flask import Blueprint, request, make_response, jsonify, url_for, abort
from pydantic import ValidationError

from api.db.crud import add_payment
from api.db.orm import Payment, Loan
from api.models.payment import PaymentModel, RefundModel
from api.auth import basic_auth

payment_blueprint = Blueprint('payment', __name__, url_prefix='/payment')

@payment_blueprint.route('/', methods=['POST'])
@basic_auth.login_required
def make_payment():
    '''
    Create payment from JSON request.
    '''
    json_data = request.get_json(force=True)

    try:
        # validate json data
        payment_data = PaymentModel(**json_data)

        # create payment and update loan balance
        loan = Loan.query.get(payment_data.loan_id)
        if loan.user_id != basic_auth.current_user().id:
            abort(403)
        
        payment = Payment(amount=payment_data.amount, loan=loan)
        add_payment(payment, loan)
        
        # create 201 response, add loan balance to payload
        payload = payment.to_dict()
        payload['loan_balance'] = loan.balance
        response = make_response(jsonify(payload), 201)
        response.headers['Location'] = url_for('payment.get_payment', id=payment.id)
        return response
    
    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)

@payment_blueprint.route('/<int:id>', methods=['GET'])
def get_payment(id):
    '''
    Retrieve payment
    '''
    return jsonify(Payment.query.get_or_404(id).to_dict())

@payment_blueprint.route('/refund', methods=['PUT'])
@basic_auth.login_required
def refund_payment():
    '''
    Refund previous payment
    '''
    json_data = request.get_json(force=True)

    try:
        refund_data = RefundModel(**json_data)

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