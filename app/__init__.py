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

from flask import request, jsonify

from .manage import default_config_app
from .JWTManager import jwt

from flask_cors import CORS
from flask_injector import FlaskInjector

from injector import Module, singleton

from flask_restful import Api
from py2neo import Graph

from .questions import ExternToolResource, GlossarioResource, ForumResource, PageResource, URLResource, FileResource, ConditionResource, QuizResource, ChatResource, LessonResource, DatabaseResource, ChoiceResource

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
        db = Graph(host="umurl.com",password=settings.PASS_DATABASE)
        self.db = db
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

    default_config_app(app)
    return app

def configureDatabase(app):
    CONFIG = {
        'password': settings.PASS_DATABASE,
    }
    #dynamic config
    app.config.from_object(settings)
    