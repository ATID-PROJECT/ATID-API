from flask import Flask

from .views import start_controller
from .modules import account_controller

from flask_migrate import Migrate
from flask_login import LoginManager

from .models import *

from dynaconf import FlaskDynaconf
from dynaconf import settings

from flask import Flask, Config
from flask.views import View
from flask_injector import FlaskInjector
from injector import inject
import os

from flask import request, jsonify
from flask_migrate import Migrate

from .JWTManager import jwt

from flask_cors import CORS
from flask_injector import FlaskInjector

from injector import Module, singleton
from .database import sqlite_db

from flask_restful import Api
from py2neo import Graph

from .questions import ExternToolResource, WikiResource, GlossarioResource, ForumResource, PageResource, URLResource, FileResource, ConditionResource, QuizResource, ChatResource, LessonResource, DatabaseResource, ChoiceResource

basedir = os.path.abspath(os.path.dirname(__file__))

class AppModule(Module):
    def __init__(self, app):
        self.app = app

    #Configure the application.
    def configure(self, binder):
        # We configure the DB here, explicitly, as Flask-SQLAlchemy requires
        # the DB to be configured before request handlers are called.
        db = self.configure_db(self.app)
        binder.bind(Graph, to=db, scope=singleton)

    def configure_db(self, app):
        db = Graph(host=settings.HOST_URL,password=settings.PASS_DATABASE)
        self.db = db
        # make anything
        return db

def create_app():
    app = Flask(__name__)
    app.config['JWT_SECRET_KEY'] = 'super-secret'
    app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:////' + os.path.join(basedir, 'data.sqlite')
    app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
    CORS(app)
    configureDatabase(app)

    jwt.init_app(app)
    
    sqlite_db.init_app(app)
    Migrate(app, sqlite_db)

    app.register_blueprint(account_controller)
    app.register_blueprint(start_controller)

    CORS(account_controller, max_age=30*86400)
    CORS(start_controller, max_age=30*86400)

    api = Api(app)
    app.url_map.strict_slashes = False

    login_manager = LoginManager()
    login_manager.session_protection = 'strong'
    login_manager.login_view = 'account_controller.login'
    login_manager.init_app(app)

    module_app = AppModule(app)
    FlaskInjector(app=app, modules=[module_app])

    api.add_resource(ForumResource, '/questions/forum/',
        resource_class_kwargs={ 'database': module_app.db })

    api.add_resource(ExternToolResource, '/questions/externtool/',
        resource_class_kwargs={ 'database': module_app.db })

    api.add_resource(FileResource, '/resources/file/',
        resource_class_kwargs={ 'database': module_app.db })

    api.add_resource(URLResource, '/resources/url/',
        resource_class_kwargs={ 'database': module_app.db })

    api.add_resource(PageResource, '/resources/page/',
        resource_class_kwargs={ 'database': module_app.db })

    api.add_resource(QuizResource, '/questions/quiz/', 
        resource_class_kwargs={ 'database': module_app.db })

    api.add_resource(WikiResource, '/questions/wiki/', 
        resource_class_kwargs={ 'database': module_app.db })

    api.add_resource(GlossarioResource, '/questions/glossario/', 
        resource_class_kwargs={ 'database': module_app.db })

    api.add_resource(ConditionResource, '/network/condition/', 
        resource_class_kwargs={ 'database': module_app.db })

    api.add_resource(ChatResource, '/questions/chat/',
        resource_class_kwargs={ 'database': module_app.db })

    api.add_resource(LessonResource, '/questions/lesson/',
        resource_class_kwargs={ 'database': module_app.db })

    api.add_resource(DatabaseResource, '/questions/database/',
        resource_class_kwargs={ 'database': module_app.db })

    api.add_resource(ChoiceResource, '/questions/choice/',
        resource_class_kwargs={ 'database': module_app.db })

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))
    
    @app.errorhandler(Exception)
    def all_exception_handler(error):
        return jsonify({"message": "Ocorreu um problema.", "status": 500}), 500

    return app

def configureDatabase(app):
    CONFIG = {
        'password': settings.PASS_DATABASE,
    }
    #dynamic config
    app.config.from_object(settings)
    