from py2neo import Graph
from dynaconf import settings

db = Graph(host=settings.HOST_URL,password=settings.PASS_DATABASE)