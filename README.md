# Payment API

This is a simple REST API designed to process loans and payments.
It is written in python and uses the Flask library as an API interface.

flask_sqlalchemy is used to interface with a SQL databsae stored locally.
pydantic is used to validate incoming json requsts.
pytest is used for unit testing.

## Environment Setup

Create Python virtual enviroment and and activate it

```bash
$ python3 -m venv .venv
$ source .venv/bin/activate
```

Install application requirements

```bash
$ make install
```

## Developing

Run unit tests

```bash
$ make test
```

To start the server locally, run

```bash
$ export FLASK_APP=api/app.py
$ make run
```

Clean up

```bash
$ make clean
```

## .env

```bash
FLASK_APP=api/app.py
FLASK_ENV=development
```

## Functionality

API routes include user, loan, and payment.
Once the server is running, a command-line client such as HTTPie can be used to
send requests to the server.

# User

Valid user credentials are required to access loan and payment functionalities.

create_user:

    PATH: {server}/user/
    METHOD: POST

    JSON format:
    {
        'username' : <str: desired username>
        'password' : <str: desired password>
    }

Login credentials must be included in the authorization header of the http request to access
loan and payment functionalities.

# Loan

create_loan:

    PATH: {server}/loan/
    METHOD: POST

    This route will create a loan. It will be linked to the current user, and only be
    accessible by them.

    JSON format:
    {
        'principal' : <float: size of loan>
    }

close_loan:

    PATH: {server}/loan/close
    METHOD: PUT

    This route will close a loan. The loan's balance must be 0, and it's status
    must be 'Open'.
    
    JSON format:
    {
        'loan_id' : <int: id of loan to close>
    }

# Payment

create_payment:

    PATH: {server}/payment/
    METHOD: POST

    This route will create a payment and update the loan balance. 
    It will be linked to the current user, and only be accessible by them.

    JSON format:
    {
        'loan_id' : <int: id of loan to pay>
        'amount'  : <float: amount of payment>
    }

refund_payment:

    PATH: {server}/payment/refund
    METHOD: PUT

    This route will refund a payment.
    The payment's status must be 'Complete' and the loan it is associated with
    must be open.

    JSON format:
    {
        'payment_id' : <int: id of payment>
    }

# Example requests (using HTTPie)

create user:
```bash
$ http POST http://127.0.0.1:5000/user username=user1 password=password123
```

create loan:
```bash
$ http --auth user1:password123 POST http://127.0.0.1:5000/loan principal=100
```

create payment:
```bash
$ http --auth user1:password123 POST http://127.0.0.1:5000/payment loan_id=1 amount=10
```

refund payment:
```bash
$ http --auth user1:password123 PUT http://127.0.0.1:5000/payment/refund payment_id=1
```

close loan:
```bash
$ http --auth user1:password123 PUT http://127.0.0.1:5000/loan/close loan_id=1
```