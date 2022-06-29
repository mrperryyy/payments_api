from optparse import check_builtin
from tabnanny import check
from api.routes.helpers import check_loan_open, check_payment_complete, check_resource_exists
from flask import Blueprint, request, make_response, jsonify, url_for, abort
from pydantic import ValidationError

from api.db.crud import add_payment, find_loan, find_payment, update_payment_status
from api.db.orm import Payment, Loan
from api.models.payment import PaymentModel, RefundModel
from api.auth import basic_auth, check_user_authentication
from api.routes.helpers import check_resource_exists, check_duplicate_payment, check_payment_less_than_balance
from api.errors import bad_request

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
    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)

    # create payment and update loan balance
    loan = find_loan(payment_data.loan_id)

    try:
        check_resource_exists(loan)
        check_user_authentication(basic_auth.current_user(), loan.user_id)
        check_duplicate_payment(loan)
        check_payment_less_than_balance(loan, payment_data.amount)
    except ValueError as error:
        print(error)
        return bad_request(str(error))
    
    payment = Payment(amount=payment_data.amount, loan=loan)
    add_payment(payment, loan)
    
    # create 201 response, add loan balance to payload
    payload = payment.to_dict()
    payload['loan_balance'] = loan.balance
    response = make_response(jsonify(payload), 201)
    response.headers['Location'] = url_for('payment.get_payment', id=payment.id)
    return response


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
    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)

    payment = find_payment(refund_data.payment_id)
    
    try:
        check_resource_exists(payment)
        loan = find_loan(payment.loan_id)
        check_user_authentication(basic_auth.current_user(), loan.user_id)
        check_payment_complete(payment)
        check_loan_open(loan)
    except ValueError as error:
        print(error)
        return bad_request(str(error))
    
    update_payment_status(payment, 'Refunded', loan)
    
    payload = payment.to_dict()
    payload['loan_balance'] = loan.balance
    response = make_response(payload, 200)
    return response
