from flask import Blueprint, request, make_response, jsonify, url_for
from pydantic import ValidationError

from api.db.crud import add_user                                                                                                                    
from api.db.orm import User
from api.models.user import UserModel
from api.routes.helpers import check_username_unique
from api.errors import bad_request, successful_response

user_blueprint = Blueprint("user", __name__, url_prefix="/user")

@user_blueprint.route("/", methods=["POST"])
def user_create_handler():
    """
    Creates a user
    """
    json_data = request.get_json(force=True)

    # validate request
    try:
        user_data = UserModel(**json_data)
    except ValidationError as error:
        print(error)
        return make_response(error.json(), 400)
    
    # check user information
    try:
        check_username_unique(user_data.username)
    except ValueError as error:
        print(error)
        return bad_request(str(error))

    # create user, update database
    user = User(username=user_data.username)
    user.set_password(user_data.password)
    add_user(user)
    
    # return 201 reponse
    return successful_response(201, user.to_dict(), location=url_for("get_loan", id=user.id))

@user_blueprint.route("/<int:id>", methods=["GET"])
def user_get_handler(id):
    return jsonify(User.query.get_or_404(id).to_dict())