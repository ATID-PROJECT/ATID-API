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
        condicao = "_.email = '{0}' AND _.passwod = '{1}'".format(email, password)
        return User.match(graph, email).where( condicao ).first()

class SubNetwork(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()
    all_data = Property()

    def create_relationship(graph, user, id_network, id_sub_network):
        graph.run("MATCH (a:Network)-[re:ATTACHMENT]-(c:User),(b:SubNetwork) WHERE a.id='{1}' and c.email='{0}' and b.uuid='{2}' create (a)-[r:SUBNETWORKS]->(b) RETURN a, b".format(user,id_network, id_sub_network)).data()

    def update_by_user(graph, user, id, id_sub, all_data):
        return graph.run("Match (p:User{email:'%s'})-[r1]-(activity:Network{id:'%s'})-[r2]-(sub:SubNetwork{uuid:'%s'}) set sub.all_data='%s'" % (user, id, id_sub, all_data))

    def fetch_by_id(graph, user, id, sub_id):
        query = "Match (p:User{email:'%s'})-[r1]-(activity:Network{id:'%s'})-[r2]-(sub:SubNetwork{uuid:'%s'}) return sub " % (user, id, sub_id)
        print( query )
        print(" ============ ")
        return graph.evaluate( query )

class Quiz(BaseModel):
    
    __primarykey__ = 'uuid'

    uuid = Property()

    name = Property()
    description = Property()
    time_limit = Property()
    time_type  = Property()
    open_date = Property()
    end_date  = Property()
    new_page = Property()
    shuffle = Property()
    
    def fetch_all_by_user(graph, email, activity, offset, limit):
        print("Match (p:User{email:'%s'})-[r]-(activity:Network{id:'%s'})-[r2]-(quiz:Quiz) return quiz SKIP %s LIMIT %s" % (email, activity, offset, limit))
        print("___________________________")
        return graph.run("Match (p:User{email:'%s'})-[r]-(activity:Network{id: '%s'})-[r2]-(quiz:Quiz) return quiz SKIP %s LIMIT %s" % (email, activity, offset, limit)).data()

class Network(BaseModel):

    __primarykey__ = 'id'

    id = Property()
    name = Property()
    course_id = Property()
    course_source = Property()
    plataform = Property()
    all_data = Property()
    
    attachment = RelatedTo(User)
    subNetworks = RelatedTo(SubNetwork)

    def getQuantity(graph, user):
        return graph.evaluate("Match (p:User{email:'%s'})-[r]-(activity:Network) return COUNT(*)" % user)

    def addQuiz(graph, user, id, quiz_id):
        return graph.run("MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (quiz:Quiz{uuid: '%s'}) CREATE (a)-[:HAS_QUESTIONS]->(quiz)" % (user ,id, quiz_id))

    def fetch_by_id(graph, user, id):
        return graph.evaluate("Match (p:User{email:'%s'})-[r]-(activity:Network{id:'%s'}) return activity " % (user, id))

    def delete_by_user(graph, user, id):
        return graph.run("Match (p:User{email:'%s'})-[r]-(activity:Network{id:'%s'}) DETACH DELETE activity " % (user, id))
        
    def update_by_user(graph, user, id, all_data, updated_at):
        return graph.run("Match (p:User{email:'%s'})-[r]-(activity:Network{id:'%s'}) set activity.all_data='%s',activity.updated_at='%s'" % (user, id, all_data, updated_at)).data()

    def fetch_all_by_user(graph, email, offset, limit):
        return graph.run("Match (p:User{email:'%s'})-[r]-(activity:Network) return activity SKIP %s LIMIT %s" % (email, offset, limit)).data()
