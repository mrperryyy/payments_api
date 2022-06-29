from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from api.config import Config
from api.routes import blueprints
from api.db.orm import db

app = Flask(__name__)
app.config.from_object(Config)
app.url_map.strict_slashes = False
for _ in map(app.register_blueprint, blueprints): ...

db.init_app(app)
with app.app_context():
    db.create_all()
migrate = Migrate(app, db)

from api import routes, models, db