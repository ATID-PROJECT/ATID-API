from py2neo import Graph
from dynaconf import settings
from flask_sqlalchemy import SQLAlchemy

db = Graph(host=settings.HOST_URL,password=settings.PASS_DATABASE)

sqlite_db = SQLAlchemy(session_options={'autocommit': False})
