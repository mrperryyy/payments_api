from flask import Blueprint, request, jsonify, url_for
from pydantic import ValidationError

from api.db.crud import add_user                                                                                                                    
from api.db.orm import User
from api.models.user import UserModel
from api.routes.helpers import check_username_unique
from api.response import bad_request, successful_response

user_blueprint = Blueprint("user", __name__, url_prefix="/user")

@user_blueprint.route("/", methods=["POST"])
def user_create_handler():
    """
    Creates a user.
    JSON format:
    {
        'username' : <str: username >
        'password' : <str: password >
    }
    """
    json_data = request.get_json(force=True)

    try:
        # validate request
        user_data = UserModel(**json_data)
    
        # check user information
        check_username_unique(user_data.username)

        # create user, update database
        user = User(username=user_data.username)
        user.set_password(user_data.password)
        add_user(user)
    
        # return 201 reponse
        return successful_response(201, user.to_dict(), location=url_for("user.user_get_handler", id=user.id))
    
    except (ValidationError, ValueError) as error:
        return bad_request(error)

@user_blueprint.route("/<int:id>", methods=["GET"])
def user_get_handler(id):
    return jsonify(User.query.get_or_404(id).to_dict())
