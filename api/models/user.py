from pydantic import BaseModel, validator
from api.db.orm import db, User
from api.db.crud import find_user

class UserModel(BaseModel):
    username: str
    password: str
