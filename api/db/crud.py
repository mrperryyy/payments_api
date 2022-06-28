from api.db.orm import db
from api.db.orm import User

def add_user(user: User) -> None:
    db.session.add(user)
    db.session.commit()