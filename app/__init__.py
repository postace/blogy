from flask import Flask
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

from config import config

db = SQLAlchemy()
jwt = JWTManager()


def create_app(config_name):
    app = Flask(__name__, template_folder="../templates")
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    # Register jwt extension
    jwt.init_app(app)

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint, url_prefix='/api')

    return app
