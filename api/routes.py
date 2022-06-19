from flask import request, make_response, jsonify, url_for
from pydantic import ValidationError

from api import app, db
from api.models import Loan, LoanValidator, Payment
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
        response = loan.to_json()
        response.status_code = 201
        response.headers['Location'] = url_for('get_loan', id=loan.id)
        return response

    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)


@app.route('/loan/<int:id>', methods=['GET'])
def get_loan(id):
    return Loan.query.get_or_404(id).to_json()