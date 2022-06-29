from flask import Blueprint, request, make_response, jsonify, url_for, abort
from pydantic import ValidationError

from api.db.crud import add_loan, update_loan_status
from api.db.orm import Loan
from api.models.loan import LoanModel, CloseLoanModel
from api.auth import basic_auth

loan_blueprint = Blueprint('loan', __name__, url_prefix='/loan')

@loan_blueprint.route('/', methods=['POST'])
@basic_auth.login_required
def create_loan():
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

        # create 201 reponse
        response = make_response(jsonify(loan.to_dict()), 201)
        response.headers['Location'] = url_for('loan.get_loan', id=loan.id)
        return response

    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)

@loan_blueprint.route('/close', methods=['POST'])
@basic_auth.login_required
def close_loan():
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

        loan = Loan.query.get(loan_data.loan_id)
        loan_must_exist(loan)
        loan_must_have_zero_balance(loan)
        loan_must_be_open(loan)
        
        if loan.user_id != basic_auth.current_user().id:
            abort(403)
        update_loan_status(loan, 'Closed')

        payload = loan.to_dict()
        response = make_response(payload, 200)
        return response

    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)

@loan_blueprint.route('/<int:id>', methods=['POST'])
def get_loan(id):
    return jsonify(Loan.query.get_or_404(id).to_dict())


def loan_must_exist(loan):
    if loan is None:
        raise ValueError(f"loan_id: {loan.id} does not exist.")

def loan_must_have_zero_balance(loan):
    if loan.balance > 0:
        raise ValueError(f"loan_id: {loan.id} balance is not zero. Current balance: {loan.balance}")

def loan_must_be_open(loan):
    if loan.status == 'Closed':
        raise ValueError(f"loan_id: {loan.id} is already closed.")
