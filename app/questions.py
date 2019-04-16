
from .views import start_controller
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from py2neo import Graph
from flask import Flask, jsonify, request, make_response
import random
import string
from py2neo import Relationship, Node

#sys.path.append("..")
from app.JWTManager import jwt
import uuid 
import sys
from flask_restful import Resource

import urllib.request, json 
from app.models import *

from injector import CallableProvider, inject

def generateUUID():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(18))

@start_controller.route('/questions/getAll', methods=['GET'])
@jwt_required
def questions_getall(db: Graph):
    current_user = get_jwt_identity()
    page = int(request.args.get("page"))-1
    size = int(request.args.get("page_size"))
    network_id = request.args.get("network_id")
    questions = db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(question) set question.label = labels(question)[0] return question SKIP %s LIMIT %s" % (current_user, network_id, page*size, size)).data()
    return jsonify(questions)

@start_controller.route('/resource/getAll', methods=['GET'])
@jwt_required
def resource_getall(db: Graph):
    current_user = get_jwt_identity()
    page = int(request.args.get("page"))-1
    size = int(request.args.get("page_size"))
    network_id = request.args.get("network_id")
    questions = db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_RESOURCE]-(resource) set resource.label = labels(resource)[0] return resource SKIP %s LIMIT %s" % (current_user, network_id, page*size, size)).data()
    return jsonify(questions)

@start_controller.route('/questions/get', methods=['GET'])
@jwt_required
def questions_get(db: Graph):
    current_user = get_jwt_identity()
    uuid = request.args.get("uuid")
    network_id = request.args.get("network_id")
    questions = db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(question{uuid: '%s'}) return question" % (current_user, network_id, uuid)).data()
    print(questions, file=sys.stderr)
    return jsonify(questions)

@start_controller.route('/resources/get', methods=['GET'])
@jwt_required
def resources_get(db: Graph):
    current_user = get_jwt_identity()
    uuid = request.args.get("uuid")
    network_id = request.args.get("network_id")
    questions = db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_RESOURCE]-(resource{uuid: '%s'}) return resource" % (current_user, network_id, uuid)).data()
    return jsonify(questions)

class Forumesource(Resource):
    
    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        forum = self.db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(forum:Forum{uuid:'%s'}) return forum" % (current_user, network_id, uuid)).data()
        return jsonify(forum)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        forum = Forum()
        forum.uuid = uuid
        forum.name = dataDict["name"]
        forum.description = dataDict["description"]
        forum.type = dataDict["type"]
        forum.max_size_upload = dataDict["max_size_upload"]
        forum.max_files = dataDict["max_files"]
        forum.show_word_count = dataDict["show_word_count"]
        forum.signature_mode = dataDict["signature_mode"]
        forum.read_monitor = dataDict["read_monitor"]
        forum.block_inactivity = dataDict["block_inactivity"]
        forum.block_duration = dataDict["block_duration"]
        forum.block_limit_messages = dataDict["block_limit_messages"]
        forum.block_limit_warning = dataDict["block_limit_warning"]
        forum.conclusion_type = dataDict["conclusion_type"]
        forum.view_required = dataDict["view_required"]
        forum.note_required = dataDict["note_required"]
        forum.messages_required = dataDict["messages_required"]
        forum.num_messages = dataDict["num_messages"]
        forum.discussion_required = dataDict["discussion_required"]
        forum.num_discussions = dataDict["num_discussions"]
        forum.replicas_required = dataDict["replicas_required"]
        forum.num_replicas = dataDict["num_replicas"]
        forum.allow_conclusion_date = dataDict["allow_conclusion_date"]
        forum.conclusion_date = dataDict["conclusion_date"]

        self.db.push(forum)

        Network.addForum(self.db, current_user, dataDict["network_id"], uuid)
        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        name = dataDict["name"]
        description = dataDict["description"]
        type = dataDict["type"]
        max_size_upload = dataDict["max_size_upload"]
        max_files = dataDict["max_files"]
        show_word_count = dataDict["show_word_count"]
        signature_mode = dataDict["signature_mode"]
        read_monitor = dataDict["read_monitor"]
        block_inactivity = dataDict["block_inactivity"]
        block_duration = dataDict["block_duration"]
        block_limit_messages = dataDict["block_limit_messages"]
        block_limit_warning = dataDict["block_limit_warning"]
        conclusion_type = dataDict["conclusion_type"]
        view_required = dataDict["view_required"]
        note_required = dataDict["note_required"]
        messages_required = dataDict["messages_required"]
        num_messages = dataDict["num_messages"]
        discussion_required = dataDict["discussion_required"]
        num_discussions = dataDict["num_discussions"]
        replicas_required = dataDict["replicas_required"]
        num_replicas = dataDict["num_replicas"]
        allow_conclusion_date = dataDict["allow_conclusion_date"]
        conclusion_date = dataDict["conclusion_date"]

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(forum:Forum{{uuid:'{uuid}'}}) \
            SET forum.name = '{name}',\
            forum.description = '{description}',\
            forum.type = '{type}',\
            forum.max_size_upload = '{max_size_upload}',\
            forum.max_files = '{max_files}',\
            forum.show_word_count = '{show_word_count}',\
            forum.signature_mode = '{signature_mode}',\
            forum.read_monitor = '{read_monitor}',\
            forum.block_inactivity = '{block_inactivity}',\
            forum.block_duration = '{block_duration}',\
            forum.block_limit_messages = '{block_limit_messages}',\
            forum.block_limit_warning = '{block_limit_warning}',\
            forum.conclusion_type = '{conclusion_type}',\
            forum.view_required = '{view_required}',\
            forum.note_required = '{note_required}',\
            forum.messages_required = '{messages_required}',\
            forum.num_messages = '{num_messages}',\
            forum.discussion_required = '{discussion_required}',\
            forum.num_discussions = '{num_discussions}',\
            forum.replicas_required = '{replicas_required}',\
            forum.num_replicas = '{num_replicas}',\
            forum.allow_conclusion_date = '{allow_conclusion_date}',\
            forum.conclusion_date = '{conclusion_date}'\
                 return forum"

        self.db.run(query).data()

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(forum:Forum{{uuid:'{uuid}'}}) DETACH DELETE forum "
        self.db.run(query)

        return jsonify({"Deleted": True})

class GlossarioResource(Resource):
    
    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        glossario = self.db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(glossario:Glossario{uuid:'%s'}) return glossario" % (current_user, network_id, uuid)).data()
        return jsonify(glossario)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        glossario = Glossario()
        glossario.uuid = uuid
        glossario.name = dataDict["name"]
        glossario.description = dataDict["description"]
        glossario.type_glossario = dataDict["type_glossario"]
        glossario.allow_new_item = dataDict["allow_new_item"]
        glossario.allow_edit = dataDict["allow_edit"]
        glossario.allow_repeat_item = dataDict["allow_repeat_item"]
        glossario.allow_comments = dataDict["allow_comments"]
        glossario.allow_automatic_links = dataDict["allow_automatic_links"]
        glossario.type_view = dataDict["type_view"]
        glossario.type_view_approved = dataDict["type_view_approved"]
        glossario.num_items_by_page = dataDict["num_items_by_page"]
        glossario.show_alphabet = dataDict["show_alphabet"]
        glossario.show_todos = dataDict["show_todos"]
        glossario.show_special = dataDict["show_special"]
        glossario.allow_print = dataDict["allow_print"]
        glossario.conclusion_type = dataDict["conclusion_type"]
        glossario.view_required = dataDict["view_required"]
        glossario.note_required = dataDict["note_required"]
        glossario.input_required = dataDict["input_required"]
        glossario.num_input = dataDict["num_input"]
        glossario.allow_conclusion_date = dataDict["allow_conclusion_date"]
        glossario.conclusion_date = dataDict["conclusion_date"]

        self.db.push(glossario)

        Network.addGlossario(self.db, current_user, dataDict["network_id"], uuid)
        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        name = dataDict["name"]
        description = dataDict["description"]
        type_glossario = dataDict["type_glossario"]
        allow_new_item = dataDict["allow_new_item"]
        allow_edit = dataDict["allow_edit"]
        allow_repeat_item = dataDict["allow_repeat_item"]
        allow_comments = dataDict["allow_comments"]
        allow_automatic_links = dataDict["allow_automatic_links"]
        type_view = dataDict["type_view"]
        type_view_approved = dataDict["type_view_approved"]
        num_items_by_page = dataDict["num_items_by_page"]
        show_alphabet = dataDict["show_alphabet"]
        show_todos = dataDict["show_todos"]
        show_special = dataDict["show_special"]
        allow_print = dataDict["allow_print"]
        conclusion_type = dataDict["conclusion_type"]
        view_required = dataDict["view_required"]
        note_required = dataDict["note_required"]
        input_required = dataDict["input_required"]
        num_input = dataDict["num_input"]
        allow_conclusion_date = dataDict["allow_conclusion_date"]
        conclusion_date = dataDict["conclusion_date"]

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(glossario:Glossario{{uuid:'{uuid}'}}) \
            SET glossario.name = '{name}',\
            glossario.description = '{description}',\
            glossario.type_glossario = '{type_glossario}',\
            glossario.allow_new_item = '{allow_new_item}',\
            glossario.allow_edit = '{allow_edit}',\
            glossario.allow_repeat_item = '{allow_repeat_item}',\
            glossario.allow_comments = '{allow_comments}',\
            glossario.allow_automatic_links = '{allow_automatic_links}',\
            glossario.type_view = '{type_view}',\
            glossario.type_view_approved = '{type_view_approved}',\
            glossario.num_items_by_page = '{num_items_by_page}',\
            glossario.show_alphabet = '{show_alphabet}',\
            glossario.show_todos = '{show_todos}',\
            glossario.show_special = '{show_special}',\
            glossario.allow_print = '{allow_print}',\
            glossario.conclusion_type = '{conclusion_type}',\
            glossario.view_required = '{view_required}',\
            glossario.input_required = '{input_required}',\
            glossario.num_input = '{num_input}',\
            glossario.allow_conclusion_date = '{allow_conclusion_date}',\
            glossario.conclusion_date = '{conclusion_date}',\
            glossario.note_required = '{note_required}'\
                 return glossario"

        self.db.run(query).data()

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(glossario:Glossario{{uuid:'{uuid}'}}) DETACH DELETE glossario "
        self.db.run(query)

        return jsonify({"Deleted": True})

class SearchResource(Resource):
    
    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        search = self.db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(search:Search{uuid:'%s'}) return search" % (current_user, network_id, uuid)).data()
        return jsonify(search)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        search = Search()
        search.uuid = uuid
        search.name = dataDict["name"]
        search.description = dataDict["description"]
        search.allow_responses_from = dataDict["allow_responses_from"]
        search.responses_from = dataDict["responses_from"]

        search.allow_responses_to = dataDict["allow_responses_to"]
        search.responses_to = dataDict["responses_to"]

        search.type_username_recorded = dataDict["type_username_recorded"]
        search.allow_mult_send = dataDict["allow_mult_send"]
        search.allow_notice_send = dataDict["allow_notice_send"]
        search.allow_automatic_numbering = dataDict["allow_automatic_numbering"]

        search.show_analyze = dataDict["show_analyze"]
        search.conclusion_message = dataDict["conclusion_message"]
        search.next_link = dataDict["next_link"]

        search.conclusion_type = dataDict["conclusion_type"]
        search.view_required = dataDict["view_required"]
        search.finished_sent = dataDict["finished_sent"]
        search.allow_conclusion_date = dataDict["allow_conclusion_date"]
        search.conclusion_date = dataDict["conclusion_date"]

        self.db.push(search)

        Network.addSearch(self.db, current_user, dataDict["network_id"], uuid)
        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        name = dataDict["name"]
        description = dataDict["description"]
        search.allow_responses_from = dataDict["allow_responses_from"]
        search.responses_from = dataDict["responses_from"]

        search.allow_responses_to = dataDict["allow_responses_to"]
        search.responses_to = dataDict["responses_to"]

        search.type_username_recorded = dataDict["type_username_recorded"]
        search.allow_mult_send = dataDict["allow_mult_send"]
        search.allow_notice_send = dataDict["allow_notice_send"]
        search.allow_automatic_numbering = dataDict["allow_automatic_numbering"]

        search.show_analyze = dataDict["show_analyze"]
        search.conclusion_message = dataDict["conclusion_message"]
        search.next_link = dataDict["next_link"]

        search.conclusion_type = dataDict["conclusion_type"]
        search.view_required = dataDict["view_required"]
        search.finished_sent = dataDict["finished_sent"]
        search.allow_conclusion_date = dataDict["allow_conclusion_date"]
        search.conclusion_date = dataDict["conclusion_date"]

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(search:Search{{uuid:'{uuid}'}}) \
            SET search.name = '{name}',\
            search.description = '{description}',\
            search.allow_responses_from = '{allow_responses_from}',\
            search.responses_from = '{responses_from}',\
            search.allow_responses_to = '{allow_responses_to}',\
            search.responses_to = '{responses_to}',\
            search.type_username_recorded = '{type_username_recorded}',\
            search.allow_mult_send = '{allow_mult_send}',\
            search.allow_notice_send = '{allow_notice_send}',\
            search.allow_automatic_numbering = '{allow_automatic_numbering}',\
            search.show_analyze = '{show_analyze}',\
            search.conclusion_message = '{conclusion_message}',\
            search.next_link = '{next_link}',\
            search.conclusion_type = '{conclusion_type}',\
            search.view_required = '{view_required}',\
            search.finished_sent = '{finished_sent}',\
            search.allow_conclusion_date = '{allow_conclusion_date}',\
            search.conclusion_date = '{conclusion_date}'\
                 return search"

        self.db.run(query).data()

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(search:Search{{uuid:'{uuid}'}}) DETACH DELETE search "
        self.db.run(query)

        return jsonify({"Deleted": True})

class URLResource(Resource):
    
    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        url = self.db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_RESOURCE]-(url:URL{uuid:'%s'}) return url" % (current_user, network_id, uuid)).data()
        return jsonify(url)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        url = URL()
        url.uuid = uuid
        url.name = dataDict["name"]
        url.description = dataDict["description"]
        url.external_url = dataDict["external_url"]

        self.db.push(url)

        Network.addURL(self.db, current_user, dataDict["network_id"], uuid)
        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        name = dataDict["name"]
        description = dataDict["description"]
        external_url = dataDict["external_url"]

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_RESOURCE]-(url:URL{{uuid:'{uuid}'}}) \
            SET url.name = '{name}',\
            url.description = '{description}',\
            url.external_url = '{external_url}',\
                 return url"

        self.db.run(query).data()

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_RESOURCE]-(url:URL{{uuid:'{uuid}'}}) DETACH DELETE url "
        self.db.run(query)

        return jsonify({"Deleted": True})

class PageResource(Resource):
    
    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        page = self.db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_RESOURCE]-(page:Page{uuid:'%s'}) return page" % (current_user, network_id, uuid)).data()
        return jsonify(page)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        page = Page()
        page.uuid = uuid
        page.name = dataDict["name"]
        page.description = dataDict["description"]
        page.content = dataDict["content"]

        self.db.push(page)

        Network.addPage(self.db, current_user, dataDict["network_id"], uuid)
        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        name = dataDict["name"]
        description = dataDict["description"]
        content = dataDict["content"]

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_RESOURCE]-(page:Page{{uuid:'{uuid}'}}) \
            SET page.name = '{name}',\
            page.description = '{description}',\
            page.content = '{content}'\
                 return file"

        self.db.run(query).data()

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_RESOURCE]-(page:Page{{uuid:'{uuid}'}}) DETACH DELETE page "
        self.db.run(query)

        return jsonify({"Deleted": True})

class FileResource(Resource):

    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        file = self.db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_RESOURCE]-(file:File{uuid:'%s'}) return file" % (current_user, network_id, uuid)).data()
        return jsonify(file)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        file = File()
        file.uuid = uuid
        file.name = dataDict["name"]
        file.description = dataDict["description"]
        file.type_display = dataDict["type_display"]
        file.type_filter_content = dataDict["type_filter_content"]

        file.show_size = dataDict["show_size"]
        file.show_type = dataDict["show_type"]
        file.show_description = dataDict["show_description"]
        file.show_resource_description = dataDict["show_resource_description"]

        self.db.push(file)

        Network.addFile(self.db, current_user, dataDict["network_id"], uuid)
        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        name = dataDict["name"]
        description = dataDict["description"]
        type_display = dataDict["type_display"]
        type_filter_content = dataDict["type_filter_content"]

        show_size = dataDict["show_size"]
        show_type = dataDict["show_type"]
        show_description = dataDict["show_description"]
        show_resource_description = dataDict["show_resource_description"]

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_RESOURCE]-(file:File{{uuid:'{uuid}'}}) \
            SET file.name = '{name}',\
            file.description = '{description}'\
            file.type_display = '{type_display}'\
            file.type_filter_content = '{type_filter_content}'\
            file.show_resource_description = '{show_resource_description}'\
                 return file"

        self.db.run(query).data()

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_RESOURCE]-(file:File{{uuid:'{uuid}'}}) DETACH DELETE file "
        self.db.run(query)

        return jsonify({"Deleted": True})

class ConditionResource(Resource):
    
    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        id_activity = request.args.get("id_activity")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        condition = self.db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_CONDITION]-(con:Condition{id_activity:'%s'}) return con" % (current_user, network_id, id_activity)).data()
        return jsonify(condition)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        print(dataDict, file=sys.stderr)
        condition = Condition()
        condition.id_activity = dataDict["id_activity"]
        condition.name_activity = dataDict["name_activity"]
        condition.data = str(dataDict["data"])

        self.db.push(condition)

        Network.addCondition(self.db, current_user, dataDict["network_id"], dataDict["id_activity"])
        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        id_activity = dataDict["id_activity"]

        name = dataDict["name_activity"]
        data = str(dataDict["data"])

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_CONDITION]-(condition:Condition{{id_activity:'{id_activity}'}}) \
            SET condition.name_activity = '{name}',\
            condition.data = '{data}' return condition"

        self.db.run(query).data()

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        id_activity = dataDict["id_activity"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_CONDITION]-(condition:Condition{{id_activity:'{id_activity}'}}) DETACH DELETE condition "
        self.db.run(query)

        return jsonify({"Deleted": True})

class QuizResource(Resource):

    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        quiz = self.db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(quiz:Quiz{uuid:'%s'}) return quiz" % (current_user, network_id, uuid)).data()
        return jsonify(quiz)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        quiz = Quiz()
        quiz.uuid = uuid
        quiz.name = dataDict["name"]
        quiz.description = dataDict["description"]
        quiz.time_limit = dataDict["time_limit"]
        quiz.time_type  = dataDict["time_type"]
        quiz.open_date = dataDict["open_date"]
        quiz.end_date  = dataDict["end_date"]
        quiz.new_page = dataDict["new_page"]
        quiz.shuffle = dataDict["shuffle"]
        quiz.allow_time_limit = dataDict["allow_time_limit"]
        quiz.allow_open_date = dataDict["allow_open_date"]
        quiz.allow_end_date = dataDict["allow_end_date"]

        self.db.push(quiz)

        Network.addQuiz(self.db, current_user, dataDict["network_id"], uuid)
        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        name = dataDict["name"]
        description = dataDict["description"]
        time_limit = dataDict["time_limit"]
        time_type  = dataDict["time_type"]
        open_date = dataDict["open_date"]
        end_date  = dataDict["end_date"]
        new_page = dataDict["new_page"]
        shuffle = dataDict["shuffle"]
        allow_time_limit = dataDict["allow_time_limit"]
        allow_open_date = dataDict["allow_open_date"]
        allow_end_date = dataDict["allow_end_date"]

        set_query = f""

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(quiz:Quiz{{uuid:'{uuid}'}}) \
             SET quiz.name = '{name}',\
            quiz.description = '{description}',\
            quiz.time_limit = '{time_limit}',\
            quiz.time_type  = '{time_type}',\
            quiz.open_date = '{open_date}',\
            quiz.end_date  = '{end_date}',\
            quiz.new_page = '{new_page}',\
            quiz.allow_time_limit = '{allow_time_limit}',\
            quiz.allow_open_date = '{allow_open_date}',\
            quiz.allow_end_date = '{allow_end_date}',\
            quiz.shuffle = '{shuffle}' return quiz"

        self.db.run(query).data()

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(quiz:Quiz{{uuid:'{uuid}'}}) DETACH DELETE quiz "
        self.db.run(query)

        return jsonify({"Deleted": True})

class ChatResource(Resource):

    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        chat = self.db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(chat:Chat{uuid:'%s'}) return chat" % (current_user, network_id, uuid)).data()
        return jsonify(chat)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        chat = Chat()
        chat.uuid = uuid
        chat.name = dataDict["name"]
        chat.description = dataDict["description"]
        self.db.push(chat)

        Network.addChat(self.db, current_user, dataDict["network_id"], uuid)
        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        name = dataDict["name"]
        description = dataDict["description"]

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(chat:Chat{{uuid:'{uuid}'}}) \
            SET chat.name = '{name}',\
            chat.description = '{description}' return chat"

        self.db.run(query).data()

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(chat:Chat{{uuid:'{uuid}'}}) DETACH DELETE chat "
        self.db.run(query)

        return jsonify({"Deleted": True})

class LessonResource(Resource):

    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        lesson = self.db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(lesson:Lesson{uuid:'%s'}) return lesson" % (current_user, network_id, uuid)).data()
        return jsonify(lesson)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        lesson = Lesson()
        lesson.uuid = uuid
        lesson.name = dataDict["name"]
        lesson.description = dataDict["description"]

        lesson.allow_revison = dataDict["allow_revison"]
        lesson.try_again = dataDict["try_again"]
        lesson.max_attempts = dataDict["max_attempts"]
        lesson.correct_action = dataDict["correct_action"]
        lesson.num_pages = dataDict["num_pages"]
        lesson.open_date = dataDict["open_date"]
        lesson.end_date = dataDict["end_date"]
        lesson.time_limit = dataDict["time_limit"]
        lesson.time_type = dataDict["time_type"]

        lesson.allow_open_date = dataDict["allow_open_date"]
        lesson.allow_end_date = dataDict["allow_end_date"]
        lesson.allow_time_limit = dataDict["allow_time_limit"]

        self.db.push(lesson)

        Network.addLesson(self.db, current_user, dataDict["network_id"], uuid)
        return jsonify({"sucess": True})
    
    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        name = dataDict["name"]
        description = dataDict["description"]

        allow_revison = dataDict["allow_revison"]
        try_again = dataDict["try_again"]
        max_attempts = dataDict["max_attempts"]
        correct_action = dataDict["correct_action"]
        num_pages = dataDict["num_pages"]
        open_date = dataDict["open_date"]
        end_date = dataDict["end_date"]
        time_limit = dataDict["time_limit"]
        time_type = dataDict["time_type"]

        allow_open_date = dataDict["allow_open_date"]
        allow_end_date = dataDict["allow_end_date"]
        allow_time_limit = dataDict["allow_time_limit"]

        set_query = f""

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(lesson:Lesson{{uuid:'{uuid}'}}) \
            SET lesson.name = '{name}',\
            lesson.description = '{description}',\
            lesson.allow_revison = '{allow_revison}',\
            lesson.try_again = '{try_again}',\
            lesson.max_attempts = '{max_attempts}',\
            lesson.correct_action = '{correct_action}',\
            lesson.num_pages = '{num_pages}',\
            lesson.open_date = '{open_date}',\
            lesson.end_date = '{end_date}',\
            lesson.time_limit = '{time_limit}',\
            lesson.time_type = '{time_type}',\
            lesson.allow_open_date = '{allow_open_date}',\
            lesson.allow_end_date = '{allow_end_date}',\
            lesson.allow_time_limit = '{allow_time_limit}'\
                 return lesson"

        self.db.run(query).data()

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(lesson:Lesson{{uuid:'{uuid}'}}) DETACH DELETE lesson "
        self.db.run(query)
class DatabaseResource(Resource):

    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        database = self.db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(database:Database{uuid:'%s'}) return database" % (current_user, network_id, uuid)).data()
        return jsonify(database)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        database = Database()
        database.uuid = uuid
        database.name = dataDict["name"]
        database.description = dataDict["description"]

        database.approval_required = dataDict["approval_required"]
        database.allow_edit_approval_entries = dataDict["allow_edit_approval_entries"]
        database.allow_comment = dataDict["allow_comment"]
        database.required_before_viewing = dataDict["required_before_viewing"]
        database.max_entries = dataDict["max_entries"]

        database.open_date = dataDict["open_date"]
        database.end_date = dataDict["end_date"]
        database.read_only = dataDict["read_only"]
        database.read_only_end = dataDict["read_only_end"]
        database.allow_read_only_end = dataDict["allow_read_only_end"]
        database.allow_read_only = dataDict["allow_read_only"]
        database.allow_open_date = dataDict["allow_open_date"]
        database.allow_end_date = dataDict["allow_end_date"]

        self.db.push(database)

        Network.addDatabase(self.db, current_user, dataDict["network_id"], uuid)
        return jsonify({"sucess": True}) 


    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        name = dataDict["name"]
        description = dataDict["description"]

        approval_required = dataDict["approval_required"]
        allow_edit_approval_entries = dataDict["allow_edit_approval_entries"]
        allow_comment = dataDict["allow_comment"]
        required_before_viewing = dataDict["required_before_viewing"]
        max_entries = dataDict["max_entries"]

        open_date = dataDict["open_date"]
        end_date = dataDict["end_date"]
        read_only = dataDict["read_only"]
        read_only_end = dataDict["read_only_end"]
        allow_read_only_end = dataDict["allow_read_only_end"]
        allow_read_only = dataDict["allow_read_only"]
        allow_open_date = dataDict["allow_open_date"]
        allow_end_date = dataDict["allow_end_date"]

        set_query = f""

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(database:Database{{uuid:'{uuid}'}}) \
            SET database.name = '{name}',\
            database.description = '{description}',\
            database.approval_required = '{approval_required}',\
            database.allow_edit_approval_entries = '{allow_edit_approval_entries}',\
            database.allow_comment = '{allow_comment}',\
            database.required_before_viewing = '{required_before_viewing}',\
            database.max_entries = '{max_entries}',\
            database.open_date = '{open_date}',\
            database.end_date = '{end_date}',\
            database.read_only = '{read_only}',\
            database.read_only_end = '{read_only_end}',\
            database.allow_read_only_end = '{allow_read_only_end}',\
            database.allow_read_only = '{allow_read_only}',\
            database.allow_open_date = '{allow_open_date}',\
            database.allow_end_date = '{allow_end_date}'\
             return database"

        self.db.run(query).data()

        Network.addQuiz(self.db, current_user, network_id, uuid)
        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(database:Database{{uuid:'{uuid}'}}) DETACH DELETE database "
        self.db.run(query)

        return jsonify({"Deleted": True})
    
class ChoiceResource(Resource):

    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        choice = self.db.run("MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(choice:Choice{uuid:'%s'}) return choice" % (current_user, network_id, uuid)).data()
        return jsonify(choice)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        choice = Choice()
        choice.uuid = uuid
        choice.name = dataDict["name"]
        choice.description = dataDict["description"]
        choice.allow_choice_update = dataDict["allow_choice_update"]
        choice.allow_multiple_choices = dataDict["allow_multiple_choices"]
        choice.allow_limit_answers = dataDict["allow_limit_answers"]
        
        choice.choice_questions = dataDict["choice_questions"]

        self.db.push(choice)

        Network.addChoice(self.db, current_user, dataDict["network_id"], uuid)
        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        name = dataDict["name"]
        description = dataDict["description"]
        allow_choice_update = dataDict["allow_choice_update"]
        allow_multiple_choices = dataDict["allow_multiple_choices"]
        allow_limit_answers = dataDict["allow_limit_answers"]
        choice_questions = dataDict["choice_questions"]

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(choice:Choice{{uuid:'{uuid}'}}) \
            SET choice.name = '{name}',\
            choice.description = '{description}',\
            choice.allow_choice_update = '{allow_choice_update}',\
            choice.allow_multiple_choices = '{allow_multiple_choices}',\
            choice.allow_limit_answers = '{allow_limit_answers}',\
            choice.choice_questions = {choice_questions}\
            return choice"

        self.db.run(query).data()

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(choice:Choice{{uuid:'{uuid}'}}) DETACH DELETE choice "
        self.db.run(query)

        return jsonify({"Deleted": True})
