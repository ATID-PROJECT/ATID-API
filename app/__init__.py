from flask import Flask
import os
import sys
import os.path as path

from .views import start_controller
from .account import account_controller

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String
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

from .manage import define_custom_commands, default_config_app
from .JWTManager import jwt

from injector import Module, singleton

from flask_cors import CORS

from ext.database import SQLAlchemy
from models.base import Model

class AppModule(Module):
    def __init__(self, app):
        self.app = app

    """Configure the application."""
    def configure(self, binder):
        # We configure the DB here, explicitly, as Flask-SQLAlchemy requires
        # the DB to be configured before request handlers are called.
        db = self.configure_db(self.app)
        define_custom_commands(self.app, db)
        binder.bind(SQLAlchemy, to=db, scope=singleton)

    def configure_db(self, app):
        db = SQLAlchemy(session_options={'autocommit': False}, Model=Model)
        db.init_app(app)
        migrate = Migrate(app, db)
        # make anything
        return db

def create_app():
    app = Flask(__name__)
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
        'type': settings.TYPE_DATABASE,
        'user': settings.USER_DATABASE,
        'password': settings.PASS_DATABASE,
        'db': settings.NAME_DATABASE,
        'host': settings.LHOST,
        'port': settings.LPORT,
    }
    if settings.TYPE_DATABASE=='sqlite':
        up =  path.abspath(path.join(__file__ ,"../.."))
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{0}/%(db)s.db'.format(up) % CONFIG
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = '%(type)s://%(user)s:\
%(password)s@%(host)s:%(port)s/%(db)s' % CONFIG
    #dynamic config
    app.config.from_object(settings)
    