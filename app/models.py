
from py2neo.ogm import GraphObject, Property, RelatedTo
import sys

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

    def fetch_network(graph, email, network_id):
        return graph.run("MATCH (u:User)-[r:ATTACHMENT]-(n:Network)\
        WHERE u.email='%s' and n.id='%s'\
        RETURN u.email" % (email, network_id)).data()

    def fetch_networks_available(graph, email, network_id):
        return graph.run("MATCH (u:User)-[r]-(n:Network)\
        WHERE u.email='%s' and n.id='%s'\
        RETURN n.id" % (email, network_id)).data()

    def fetchSharedUser(graph, email, network_id):
        return graph.run("MATCH (u)-[rel:sharing]->(n) \
        WHERE u.email='%s' AND n.id='%s' \
        RETURN u" % (email, network_id)).data()

    def secure_fetch_by_email(graph, email):
        result = graph.run(
            "MATCH (user:User) where user.email='%s' REMOVE user.password RETURN user" %
            (email)).data()
        return result

    def unshare(graph, email, network_id):
        graph.run("MATCH (u)-[rel:sharing]->(n) \
        WHERE u.email='%s' AND n.id='%s' \
        DELETE rel" % (email, network_id)).data()

    def sharingNetworkAccess(graph, id_network):
        result = graph.run(
            "MATCH (user:User)-[s:sharing]-(n:Network{id:'%s'}) return user" %
            (id_network)).data()
        return result

    def addNetworkShared(graph, email, id_network):
        graph.run(
            "MATCH (u:User),(n:Network) WHERE u.email='%s' and n.id='%s' \
        create (u)-[s:sharing]->(n)" %
            (email, id_network)).data()

    def fetch_by_email_and_password(graph, email, password):
        condicao = "_.email = '{0}' AND _.passwod = '{1}'".format(
            email, password)
        return User.match(graph, email).where(condicao).first()


class Course(BaseModel):

    __primarykey__ = 'id'

    id = Property()
    fullname = Property()
    shortname = Property()
    network_id = Property()

    def get_length(graph, user):
        return graph.run(
            "MATCH (p:User{email:'%s'})-[r]-(activity)-[r2]-(course:Course) return COUNT(DISTINCT course) as total" %
            user).data()

    def fetch_all_by_user(graph, email, offset, limit):
        return graph.run(
            "Match (p:User{email:'%s'})-[r]-(activity:Course) return activity ORDER BY id DESC SKIP %s LIMIT %s" %
            (email, offset, limit)).data()

    def fetch_by_id(graph, user, id):
        return graph.evaluate(
            "Match (p:User{email:'%s'})-[r]-(activity)-[r2]-(course:Course{id:'%s'}) return course " %
            (user, id))

    def addChat(graph, user, course_id, chat_id):
        oi = "MATCH (u:User {email:'%s'})-[r]-(a:Network)-[r2]-(course:Course{id:%d}), (chat:ChatInstance{uuid: '%s'}) CREATE (course)-[:HAS_INSTANCE]->(chat)" % (
            user, int(course_id), chat_id)
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network)-[r2]-(course:Course{id:%d}), (chat:ChatInstance{uuid: '%s'}) CREATE (course)-[:HAS_INSTANCE]->(chat)" %
            (user, int(course_id), chat_id))

    def addDatabase(graph, user, course_id, data_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network)-[r2]-(course:Course{id:%s}), (database:DatabaseInstance{uuid: '%s'}) CREATE (course)-[:HAS_INSTANCE]->(database)" %
            (user, course_id, data_id))

    def addForum(graph, user, course_id, forum_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network)-[r2]-(course:Course{id:%s}), (forum:ForumInstance{uuid: '%s'}) CREATE (course)-[:HAS_INSTANCE]->(forum)" %
            (user, course_id, forum_id))

    def addExternTool(graph, user, course_id, lti_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network)-[r2]-(course:Course{id:%s}), (lti:ExternToolInstance{uuid: '%s'}) CREATE (course)-[:HAS_INSTANCE]->(lti)" %
            (user, course_id, lti_id))

    def addGlossario(graph, user, course_id, glossario_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network)-[r2]-(course:Course{id:%s}), (glossario:GlossarioInstance{uuid: '%s'}) CREATE (course)-[:HAS_INSTANCE]->(glossario)" %
            (user, course_id, glossario_id))

    def addWiki(graph, user, course_id, wiki_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network)-[r2]-(course:Course{id:%s}), (wiki:WikiInstance{uuid: '%s'}) CREATE (course)-[:HAS_INSTANCE]->(wiki)" %
            (user, course_id, wiki_id))

    def addChoice(graph, user, course_id, choice_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network)-[r2]-(course:Course{id:%s}), (choice:ChoiceInstance{uuid: '%s'}) CREATE (course)-[:HAS_INSTANCE]->(choice)" %
            (user, course_id, choice_id))

    def addQuiz(graph, user, course_id, quiz_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network)-[r2]-(course:Course{id:%s}), (quiz:QuizInstance{uuid: '%s'}) CREATE (course)-[:HAS_INSTANCE]->(quiz)" %
            (user, course_id, quiz_id))

    def delete_by_user(graph, user, id):
        return graph.run(
            "Match (p:User{email:'%s'})-[r]-(:Network)-[r2]-(course:Course{id:%s}) DETACH DELETE course " %
            (user, id))


class SubNetwork(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()
    all_data = Property()

    def create_relationship(graph, user, id_network, id_sub_network):
        graph.run(
            "MATCH (a:Network)-[re:ATTACHMENT]-(c:User),(b:SubNetwork) WHERE a.id='{1}' and c.email='{0}' and b.uuid='{2}' create (a)-[r:SUBNETWORKS]->(b) RETURN a, b".format(
                user,
                id_network,
                id_sub_network)).data()

    def update_by_user(graph, user, id, id_sub, all_data):
        return graph.run(
            "Match (p:User{email:'%s'})-[r1]-(activity:Network{id:'%s'})-[r2]-(sub:SubNetwork{uuid:'%s'}) set sub.all_data='%s'" %
            (user, id, id_sub, all_data))

    def fetch_by_id(graph, user, id, sub_id):
        query = "Match (p:User{email:'%s'})-[r1]-(activity:Network{id:'%s'})-[r2]-(sub:SubNetwork{uuid:'%s'}) return sub " % (
            user, id, sub_id)
        return graph.evaluate(query)


class Quiz(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    name = Property()
    label = Property()
    description = Property()
    time_limit = Property()
    time_type = Property()
    open_date = Property()
    end_date = Property()
    new_page = Property()
    shuffle = Property()
    allow_time_limit = Property()
    allow_open_date = Property()
    allow_end_date = Property()

    has_trigged = Property()

    def fetch_all_by_user(graph, email, activity, offset, limit):
        return graph.run(
            "Match (p:User{email:'%s'})-[r]-(activity:Network{id: '%s'})-[r2]-(quiz:Quiz) return quiz SKIP %s LIMIT %s" %
            (email, activity, offset, limit)).data()


class QuizInstance(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    id_quiz = Property()
    id_instance = Property()
    id_group = Property()


class Chat(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    name = Property()
    label = Property()
    description = Property()


class ChatInstance(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    id_chat = Property()
    id_instance = Property()
    id_group = Property()


class Wiki(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    name = Property()
    label = Property()
    description = Property()
    wikimode = Property()
    firstpagetitle = Property()
    defaultformat = Property()


class WikiInstance(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    id_wiki = Property()
    id_instance = Property()
    id_group = Property()


class File(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    name = Property()
    label = Property()
    description = Property()
    type_display = Property()
    type_filter_content = Property()

    # boolean variables
    show_size = Property()
    show_type = Property()
    show_description = Property()
    show_resource_description = Property()


class Forum(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    name = Property()
    label = Property()
    description = Property()
    type_forum = Property()

    maxbytes = Property()
    maxattachments = Property()
    displaywordcount = Property()
    forcesubscribe = Property()
    trackingtype = Property()


class ForumInstance(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    id_forum = Property()
    id_instance = Property()
    id_group = Property()


class Glossario(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    name = Property()
    label = Property()
    description = Property()
    type_glossario = Property()

    allow_new_item = Property()
    allow_edit = Property()
    allow_repeat_item = Property()
    allow_comments = Property()
    allow_automatic_links = Property()

    type_view = Property()
    type_view_approved = Property()
    num_items_by_page = Property()
    show_alphabet = Property()
    show_todos = Property()
    show_special = Property()
    allow_print = Property()

    conclusion_type = Property()
    view_required = Property()
    note_required = Property()
    entry_required = Property()
    entry_value = Property()
    conclusion_date = Property()


class GlossarioInstance(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()
    label = Property()

    id_glossario = Property()
    id_instance = Property()
    id_group = Property()


class Search(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    label = Property()
    name = Property()
    description = Property()

    allow_responses_from = Property()
    responses_from = Property()

    allow_responses_to = Property()
    responses_to = Property()

    type_username_recorded = Property()
    allow_mult_send = Property()
    allow_notice_send = Property()
    allow_automatic_numbering = Property()

    show_analyze = Property()
    conclusion_message = Property()
    next_link = Property()

    conclusion_type = Property()
    view_required = Property()
    finished_sent = Property()
    allow_conclusion_date = Property()
    conclusion_date = Property()


class URL(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    name = Property()
    external_url = Property()
    description = Property()


class Page(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    name = Property()
    description = Property()
    content = Property()


class ExternTool(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    name = Property()
    label = Property()
    description = Property()
    show_description_course = Property()
    show_activity = Property()
    show_description_activity = Property()

    pre_config_url = Property()
    url_tool = Property()
    url_tool_ssl = Property()

    pre_config = Property()
    key_consumer = Property()
    key_secret = Property()
    custom_params = Property()

    share_name = Property()
    share_email = Property()
    accept_notes = Property()


class ExternToolInstance(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    id_extern_tool = Property()
    id_instance = Property()
    id_group = Property()


class Lesson(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    name = Property()
    label = Property()
    description = Property()
    allow_revison = Property()
    try_again = Property()
    max_attempts = Property()
    correct_action = Property()
    num_pages = Property()
    open_date = Property()
    end_date = Property()
    time_limit = Property()
    time_type = Property()

    allow_open_date = Property()
    allow_end_date = Property()
    allow_time_limit = Property()


class Condition(BaseModel):

    __primarykey__ = 'id_transiction'

    id_activity = Property()
    id_transiction = Property()
    name_activity = Property()
    data = Property()


class Choice(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    name = Property()
    label = Property()
    description = Property()
    allow_choice_update = Property()
    allow_multiple_choices = Property()
    allow_limit_answers = Property()
    choice_questions = Property()


class ChoiceInstance(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    id_choice = Property()
    id_instance = Property()
    id_group = Property()


class Database(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()
    name = Property()
    label = Property()
    description = Property()

    approval_required = Property()
    allow_edit_approval_entries = Property()
    allow_comment = Property()
    required_before_viewing = Property()
    max_entries = Property()

    open_date = Property()
    end_date = Property()
    read_only = Property()
    read_only_end = Property()

    allow_read_only_end = Property()
    allow_read_only = Property()
    allow_open_date = Property()
    allow_end_date = Property()


class DatabaseInstance(BaseModel):

    __primarykey__ = 'uuid'

    uuid = Property()

    id_database = Property()
    id_instance = Property()
    id_group = Property()


class Network(BaseModel):

    __primarykey__ = 'id'

    id = Property()
    name = Property()
    token = Property()
    url = Property()
    course_id = Property()
    course_source = Property()
    plataform = Property()
    all_data = Property()

    attachment = RelatedTo(User)
    subNetworks = RelatedTo(SubNetwork)

    def get_length(graph, user):
        return graph.run(
            "MATCH (p:User{email:'%s'})-[r]-(net:Network) return COUNT(DISTINCT net) as total" %
            user).data()

    def getActivity(graph, user, activity_uuid, activity_type):
        return graph.run(
            f"MATCH (u:User {{email:'{user}'}})-[r]-(:Network)-[:HAS_QUESTIONS]-\
        (activity:{activity_type}{{uuid: '{activity_uuid}'}}) return activity").data()

    def getQuantity(graph, user):
        return graph.evaluate(
            "Match (p:User{email:'%s'})-[r]-(activity:Network) return COUNT(*)" %
            user)

    def addSearch(graph, user, id, search_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (search:Search{uuid: '%s'}) CREATE (a)-[:HAS_QUESTIONS]->(search)" %
            (user, id, search_id))

    def addCourse(graph, user, id, course_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (course:Course{id: %s}) CREATE (a)-[:HAS_COURSE]->(course)" %
            (user, id, course_id))

    def addExternTool(graph, user, id, externtool_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (externtool:ExternTool{uuid: '%s'}) CREATE (a)-[:HAS_QUESTIONS]->(externtool)" %
            (user, id, externtool_id))

    def addGlossario(graph, user, id, glossario_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (glossario:Glossario{uuid: '%s'}) CREATE (a)-[:HAS_QUESTIONS]->(glossario)" %
            (user, id, glossario_id))

    def addQuiz(graph, user, id, quiz_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (quiz:Quiz{uuid: '%s'}) CREATE (a)-[:HAS_QUESTIONS]->(quiz)" %
            (user, id, quiz_id))

    def addForum(graph, user, id, forum_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (forum:Forum{uuid: '%s'}) CREATE (a)-[:HAS_QUESTIONS]->(forum)" %
            (user, id, forum_id))

    def addCondition(graph, user, id, condition_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (condition:Condition{id_transiction: '%s'}) CREATE (a)-[:HAS_CONDITION]->(condition)" %
            (user, id, condition_id))

    def addChat(graph, user, id, chat_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (chat:Chat{uuid: '%s'}) CREATE (a)-[:HAS_QUESTIONS]->(chat)" %
            (user, id, chat_id))

    def addWiki(graph, user, id, wiki_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (wiki:Wiki{uuid: '%s'}) CREATE (a)-[:HAS_QUESTIONS]->(wiki)" %
            (user, id, wiki_id))

    def addFile(graph, user, id, file_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (file:File{uuid: '%s'}) CREATE (a)-[:HAS_RESOURCE]->(file)" %
            (user, id, file_id))

    def addPage(graph, user, id, page_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (page:Page{uuid: '%s'}) CREATE (a)-[:HAS_RESOURCE]->(page)" %
            (user, id, page_id))

    def addURL(graph, user, id, url_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (url:URL{uuid: '%s'}) CREATE (a)-[:HAS_RESOURCE]->(url)" %
            (user, id, url_id))

    def addChoice(graph, user, id, choice_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (choice:Choice{uuid: '%s'}) CREATE (a)-[:HAS_QUESTIONS]->(choice)" %
            (user, id, choice_id))

    def addLesson(graph, user, id, lesson_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (lesson:Lesson{uuid: '%s'}) CREATE (a)-[:HAS_QUESTIONS]->(lesson)" %
            (user, id, lesson_id))

    def addDatabase(graph, user, id, database_id):
        return graph.run(
            "MATCH (u:User {email:'%s'})-[r]-(a:Network {id:'%s'}), (database:Database{uuid: '%s'}) CREATE (a)-[:HAS_QUESTIONS]->(database)" %
            (user, id, database_id))

    def fetch_by_id(graph, user, id):
        return graph.evaluate(
            "Match (p:User{email:'%s'})-[r]-(activity:Network{id:'%s'}) return activity " %
            (user, id))

    def delete_by_user(graph, user, id):
        return graph.run(
            "Match (p:User{email:'%s'})-[r]-(activity:Network{id:'%s'}) DETACH DELETE activity " %
            (user, id))

    def update_by_user(graph, user, id, all_data, updated_at):
        return graph.run(
            "Match (p:User{email:'%s'})-[r]-(activity:Network{id:'%s'}) set activity.all_data='%s',activity.updated_at='%s'" %
            (user, id, all_data, updated_at)).data()

    def update_name_by_user(graph, user, id, new_name, updated_at):
        return graph.run(
            "Match (p:User{email:'%s'})-[r]-(activity:Network{id:'%s'}) set activity.name='%s',activity.updated_at='%s'" %
            (user, id, new_name, updated_at)).data()

    def fetch_all_by_user(graph, email, offset, limit, code, name):
        # return graph.run("Match (p:User{email:'%s'})-[r]-(activity:Network)
        # return activity SKIP %s LIMIT %s" % (email, offset, limit)).data()
        print(f"Match (p:User{{email:'{email}'}})-[r]-(activity:Network) where toLower(activity.id) =~ toLower('.*{code}.*') and toLower(activity.name) =~ toLower('.*{name}.*') return activity SKIP {offset} LIMIT {limit}", file=sys.stderr)
        return graph.run(
            f"Match (p:User{{email:'{email}'}})-[r]-(activity:Network) where toLower(activity.id) =~ toLower('.*{code}.*') and toLower(activity.name) =~ toLower('.*{name}.*') return activity SKIP {offset} LIMIT {limit}").data()
