from flask import Blueprint, request, jsonify, url_for
from pydantic import ValidationError

from api.db.crud import add_loan, find_loan, update_loan_status
from api.db.orm import Loan
from api.models.loan import LoanModel, CloseLoanModel
from api.routes.helpers import check_resource_exists, check_loan_open, check_loan_empty_balance
from api.auth import basic_auth, check_user_authentication
from api.response import bad_request, successful_response

loan_blueprint = Blueprint('loan', __name__, url_prefix='/loan')

@loan_blueprint.route('/', methods=['POST'])
@basic_auth.login_required
def loan_create_handler():
    '''
    Creates a loan.
    JSON format:
    {
        'principal' : <float: loan principal>
    }
    '''
    json_data = request.get_json(force=True)

    try:
        # validate request
        loan_data = LoanModel(**json_data)

        # create loan
        loan = Loan(principal=loan_data.principal, balance=loan_data.principal, user=basic_auth.current_user())
        add_loan(loan)

        # return 201 reponse
        return successful_response(201, loan.to_dict(), location=url_for('loan.loan_get_handler', id=loan.id))
    
    except (ValidationError, ValueError) as error:
        return bad_request(error)


@loan_blueprint.route('/close', methods=['PUT'])
@basic_auth.login_required
def loan_close_handler():
    '''
    Closes loan. Balance must be 0.
    JSON format:
    {
        'loan_id' : <int: loan id >
    }
    '''
    json_data = request.get_json(force=True)

    try:
        # validate request
        loan_data = CloseLoanModel(**json_data)

        # retrieve loan from database
        loan = find_loan(loan_data.loan_id)
    
        # check loan
        check_resource_exists(loan)
        check_user_authentication(basic_auth.current_user(), loan.user_id)
        check_loan_empty_balance(loan)
        check_loan_open(loan)

        # update database
        update_loan_status(loan, 'Closed')

        # return 200 response
        return successful_response(200, loan.to_dict())
    
    except (ValidationError, ValueError) as error:
        return bad_request(error)

@loan_blueprint.route('/<int:id>', methods=['GET'])
def loan_get_handler(id):
    return jsonify(Loan.query.get_or_404(id).to_dict())
