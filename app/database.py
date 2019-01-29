from py2neo import Graph
from dynaconf import settings

db = Graph(host="umurl.com",password=settings.PASS_DATABASE)