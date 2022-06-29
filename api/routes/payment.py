from optparse import check_builtin
from tabnanny import check
from api.routes.helpers import check_loan_open, check_payment_complete, check_resource_exists
from flask import Blueprint, request, jsonify, url_for
from pydantic import ValidationError

from api.db.crud import add_payment, find_loan, find_payment, update_payment_status
from api.db.orm import Payment, Loan
from api.models.payment import PaymentModel, RefundModel
from api.auth import basic_auth, check_user_authentication
from api.routes.helpers import check_resource_exists, check_duplicate_payment, check_payment_less_than_balance
from api.response import bad_request, successful_response

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

        # retrieve loan
        loan = find_loan(payment_data.loan_id)

        # check loan information
        check_resource_exists(loan)
        check_user_authentication(basic_auth.current_user(), loan.user_id)
        check_duplicate_payment(loan, payment_data.amount)
        check_payment_less_than_balance(loan, payment_data.amount)
    
        # create payment, update database
        payment = Payment(amount=payment_data.amount, loan=loan)
        add_payment(payment, loan)

        # return 201 response
        payload = payment.to_dict()
        payload['loan_balance'] = loan.balance
        return successful_response(201, payload, location=url_for('payment.get_payment', id=payment.id))
    
    except (ValidationError, ValueError) as error:
        return bad_request(error)


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
        # validate json data
        refund_data = RefundModel(**json_data)

        # retrieve payment
        payment = find_payment(refund_data.payment_id)
    
        # check payment information
        check_resource_exists(payment)
        loan = find_loan(payment.loan_id)
        check_user_authentication(basic_auth.current_user(), loan.user_id)
        check_payment_complete(payment)
        check_loan_open(loan)
    
        # update database
        update_payment_status(payment, 'Refunded', loan=loan)

        # return 200 response
        payload = payment.to_dict()
        payload['loan_balance'] = loan.balance
        return successful_response(200, payload)
    
    except (ValidationError, ValueError) as error:
        return bad_request(error)
