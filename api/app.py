from flask import Flask
from api.config import Config
from api.routes import blueprints
from api.db.orm import db

from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(Config)
app.url_map.strict_slashes = False
db.init_app(app)
migrate = Migrate(app, db)

for _ in map(app.register_blueprint, blueprints): ...
