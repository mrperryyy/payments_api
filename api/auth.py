from flask import abort
from flask_httpauth import HTTPBasicAuth
from api.db.orm import User
from api.response import error_response

basic_auth = HTTPBasicAuth()

@basic_auth.verify_password
def verify_password(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        return user

@basic_auth.error_handler
def basic_auth_error(status):
    return error_response(status)

def check_user_authentication(current_user: User, id: int) -> None:
    if id != current_user.id:
        abort(403)
