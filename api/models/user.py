from pydantic import BaseModel, validator
from api.db.orm import db, User

class UserModel(BaseModel):
    username: str
    password: str

    # TODO: move this somewhere else, helper function
    @validator('username')
    def username_must_be_unique(cls, username):
        if db.session.query(User).filter_by(username=username).first() is not None:
            raise ValueError(f"Username {username} is already in use.")
        return username