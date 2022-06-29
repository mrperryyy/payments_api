from pydantic import BaseModel, validator
from api.db.orm import db, User
from api.db.crud import find_user

class UserModel(BaseModel):
    username: str
    password: str

    # TODO: move this somewhere else, helper function
    @validator('username')
    def username_must_be_unique(cls, username):
        if find_user(username) is not None:
            raise ValueError(f"Username {username} is already in use.")
        return username