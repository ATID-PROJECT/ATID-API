import maya

from py2neo.ogm import GraphObject, Property, RelatedTo

class BaseModel(GraphObject):
    """
    Implements some basic functions to guarantee some standard functionality
    across all models. The main purpose here is also to compensate for some
    missing basic features that we expected from GraphObjects, and improve the
    way we interact with them.
    """
    created_at = Property()
    updated_at = Property()

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

class SubActivity(BaseModel):

    __primarykey__ = 'id'

    id = Property()
    all_data = Property()

    def fetch_by_id(graph, user, id, sub_id):
        return graph.run("Match (p:User{email:'%s'})-[r]-(activity:Activity{id:'%s'})-[r]-(sub:SubActivity{id:'%s'}) return sub.id,sub.all_data " % (user, id, sub_id)).data()

class Activity(BaseModel):

    __primarykey__ = 'id'

    id = Property()
    name = Property()
    all_data = Property()
    
    attachment = RelatedTo(User)
    subNetworks = RelatedTo(SubActivity)

    def fetch_by_id(graph, user, id):
        return graph.run("Match (p:User{email:'%s'})-[r]-(activity:Activity{id:'%s'}) return activity.id,activity.name,activity.all_data " % (user, id)).data()

    def update_by_user(graph, user, id, all_data):
        return graph.run("Match (p:User{email:'%s'})-[r]-(activity:Activity{id:'%s'}) set activity.all_data='%s'" % (user, id, all_data)).data()

    def fetch_all_by_user(graph, email, offset, limit):
        return graph.run("Match (p:User{email:'%s'})-[r]-(activity:Activity) return activity.id,activity.name SKIP %s LIMIT %s" % (email, offset, limit)).data()
