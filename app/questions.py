
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

import urllib.request, json 
from app.models import *

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

@start_controller.route('/questions/quiz/register', methods=['POST'])
@jwt_required
def add_quiz(db: Graph):
    dataDict = json.loads(request.data)
    current_user = get_jwt_identity()
    uuid = generateUUID()

    quiz = Quiz()
    quiz.uuid = uuid
    quiz.name = dataDict["name"]
    description = dataDict["description"]
    time_limit = dataDict["time_limit"]
    time_type  = dataDict["time_type"]
    open_date = dataDict["open_date"]
    end_date  = dataDict["end_date"]
    new_page = dataDict["new_page"]
    shuffle = dataDict["shuffle"]
    db.push(quiz)

    Network.addQuiz(db, current_user, dataDict["id_network"], uuid)
    return jsonify({"sucess": True})

@start_controller.route('/questions/chat/register', methods=['POST'])
@jwt_required
def add_chat(db: Graph):
    dataDict = json.loads(request.data)
    current_user = get_jwt_identity()
    uuid = generateUUID()

    chat = Chat()
    chat.uuid = uuid
    chat.name = dataDict["name"]
    chat.description = dataDict["description"]
    db.push(chat)

    Network.addChat(db, current_user, dataDict["id_network"], uuid)
    return jsonify({"sucess": True})

@start_controller.route('/questions/lesson/register', methods=['POST'])
@jwt_required
def add_lesson(db: Graph):
    dataDict = json.loads(request.data)
    current_user = get_jwt_identity()
    uuid = generateUUID()

    lesson = Lesson()
    lesson.uuid = uuid
    lesson.name = dataDict["name"]
    lesson.description = dataDict["description"]

    lesson.allow_revison = dataDict["allow_revison"]
    lesson.try_again = dataDict["try_again"]
    lesson.max_tnumber = dataDict["max_tnumber"]
    lesson.correct_action = dataDict["correct_action"]
    lesson.num_pages = dataDict["num_pages"]
    lesson.open_date = dataDict["open_date"]
    lesson.end_date = dataDict["end_date"]
    lesson.limit_time = dataDict["limit_time"]
    lesson.time_format = dataDict["time_format"]

    lesson.check_open_date = dataDict["check_open_date"]
    lesson.check_end_date = dataDict["check_end_date"]
    lesson.check_format = dataDict["check_format"]

    db.push(lesson)

    Network.addLesson(db, current_user, dataDict["id_network"], uuid)
    return jsonify({"sucess": True})

@start_controller.route('/questions/database/register', methods=['POST'])
@jwt_required
def add_database(db: Graph):
    dataDict = json.loads(request.data)
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
    database.check_read_only_end = dataDict["check_read_only_end"]
    database.check_read_only = dataDict["check_read_only"]
    database.check_open_date = dataDict["check_open_date"]
    database.check_end_date = dataDict["check_end_date"]

    db.push(database)

    Network.addDatabase(db, current_user, dataDict["id_network"], uuid)
    return jsonify({"sucess": True})