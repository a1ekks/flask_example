from flask import Flask, current_app
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from config import config
from flask_principal import Principal, identity_loaded
from .tools.database import db
from .auth.views import before_request
from .auth.login import login_manager


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    db.init_app(app)
    login_manager.init_app(app)
    Principal(app)


    # register apps
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app

