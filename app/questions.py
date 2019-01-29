
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
    print(questions, file=sys.stderr)
    return jsonify(questions)

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
        quiz.allow_open_data = dataDict["allow_open_data"]
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
        allow_open_data = dataDict["allow_open_data"]
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
            quiz.allow_open_data = '{allow_open_data}',\
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

        lesson.allow_open_data = dataDict["allow_open_data"]
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

        allow_open_data = dataDict["allow_open_data"]
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
            lesson.allow_open_data = '{allow_open_data}',\
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