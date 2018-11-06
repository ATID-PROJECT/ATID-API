import maya

from py2neo.ogm import GraphObject, Property, RelatedTo

class BaseModel(GraphObject):
    """
    Implements some basic functions to guarantee some standard functionality
    across all models. The main purpose here is also to compensate for some
    missing basic features that we expected from GraphObjects, and improve the
    way we interact with them.
    """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
class User(BaseModel):

    __primarykey__ = 'email'

    email = Property()
    first_name = Property()
    last_name = Property()
    passwod = Property()

    def as_dict(self):
        return {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
        }

    def fetch_by_email(graph, email):
        return User.match(graph, email).first()

    def fetch_by_email_and_password(graph, email, password):
        return User.match(graph, email).where(
            f'_.email = "{email}" AND _.passwod = "{password}"'
        ).first()

    def fetch(self, graph):
        return self.select(graph, self.email).first()

class Activity(BaseModel):

    __primarykey__ = 'name'

    name = Property()
    all_data = Property()

    attachment = RelatedTo(User)