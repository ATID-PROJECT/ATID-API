from flask import Flask

from .views import start_controller
from .account import account_controller

from flask_migrate import Migrate
from flask_login import LoginManager

from .models import *

from dynaconf import FlaskDynaconf
from dynaconf import settings

from flask import Flask, Config
from flask.views import View
from flask_injector import FlaskInjector
from injector import inject

from flask import request

from .manage import default_config_app
from .JWTManager import jwt

from flask_cors import CORS
from flask_injector import FlaskInjector
from py2neo import Graph
from injector import Module, singleton
class AppModule(Module):
    def __init__(self, app):
        self.app = app

    """Configure the application."""
    def configure(self, binder):
        # We configure the DB here, explicitly, as Flask-SQLAlchemy requires
        # the DB to be configured before request handlers are called.
        db = self.configure_db(self.app)
        binder.bind(Graph, to=db, scope=singleton)

    def configure_db(self, app):
        db = Graph(host="umurl.com",password='admin')
        # make anything
        return db

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'super-secret'
    CORS(app)
    configureDatabase(app)

    jwt.init_app(app)
    
    app.register_blueprint(account_controller)
    app.register_blueprint(start_controller)

    FlaskInjector(app=app, modules=[AppModule(app)])

    app.url_map.strict_slashes = False

    login_manager = LoginManager()
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'account_controller.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    default_config_app(app)
    return app

def configureDatabase(app):
    CONFIG = {
        'password': settings.PASS_DATABASE,
    }
    #dynamic config
    app.config.from_object(settings)
    