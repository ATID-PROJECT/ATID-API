# coding: utf-8
from dynaconf import settings
from flask import Blueprint, render_template, request, jsonify
from .models import *
import random
import string
from py2neo import Graph
from flask_login import current_user, login_required, logout_user, login_user
from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity,
)

from app.JWTManager import jwt
from py2neo import Relationship, Node
from .modules.controller import create_course
from app.modules.controller import createQuestion
from app.sqlite_models import *

import sys
import requests

from app.modules.general.course import get_enrolled

import uuid
import os
from flask_restful import Resource

from app.logManager import createLog
import urllib.request, json
from app.models import *
from .modules.general.quiz_status import getQuizStatus
from .modules.general.attemps_events import getAttempsStatus

from .modules import *
from .modules.activitys import *

from .modules.controller import createGroup

from .modules.general.course import getCourseByName, getUsersByCourse

from injector import CallableProvider, inject

start_controller = Blueprint("start_controller", __name__, template_folder="templates")


def generateUUID():
    return "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(18)
    )


@start_controller.route("/")
def index(db: Graph):
    o = request.remote_addr
    host = o
    print(host + "...", file=sys.stderr)
    return "API ATID"


@start_controller.route("/activity_analyze")
@jwt_required
def activity_analyze(db: Graph):

    try:
        current_user = get_jwt_identity()

        course_id = request.args.get("course_id")
        network_id = request.args.get("network_id")
        activity_id = request.args.get("activity_id")

        quiz_info = "MATCH (c:Course)-[]-(n) where c.id = {} and n.id_quiz='{}' return n".format(
            course_id, activity_id
        )
        id_quiz = db.run(quiz_info).data()[0]["n"]["id_instance"]
        quiz_instance = db.run(
            "MATCH (c:Course)-[r]-(n:QuizInstance) where n.id_quiz='%s' and c.id=%s RETURN n"
            % (activity_id, course_id)
        ).data()[0]["n"]

        network = db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(net:Network{id:'%s'}) return net"
            % (current_user, network_id)
        ).data()[0]["net"]

        result = getQuizStatus(
            network["url"], network["token"], course_id, quiz_instance["id_instance"]
        )
        return jsonify(result)

    except Exception as e:
        return jsonify([])


@start_controller.route("/attemps_analyze")
@jwt_required
def attemps_analyze(db: Graph):
    try:
        current_user = get_jwt_identity()

        course_id = request.args.get("course_id")
        network_id = request.args.get("network_id")
        activity_id = request.args.get("activity_id")

        quiz_info = "MATCH (c:Course)-[]-(n) where c.id = {} and n.id_quiz='{}' return n".format(
            course_id, activity_id
        )
        id_quiz = db.run(quiz_info).data()[0]["n"]["id_instance"]
        quiz_instance = db.run(
            "MATCH (c:Course)-[r]-(n:QuizInstance) where n.id_quiz='%s' and c.id=%s RETURN n"
            % (activity_id, course_id)
        ).data()[0]["n"]

        network = db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(net:Network{id:'%s'}) return net"
            % (current_user, network_id)
        ).data()[0]["net"]

        result = getAttempsStatus(
            network["url"], network["token"], course_id, quiz_instance["id_instance"]
        )
        return jsonify(result)

    except Exception as e:
        return jsonify([])


@start_controller.route("/get_enrolled_users", methods=["GET", "POST"])
@jwt_required
def get_enrolled_users(db: Graph):
    current_user = get_jwt_identity()

    network_id = request.args.get("network_id")
    course_id = request.args.get("course_id")

    result = get_enrolled(db, current_user, network_id, course_id)

    return jsonify(result)


@start_controller.route("/questions/getAll", methods=["GET"])
@jwt_required
def questions_getall(db: Graph):
    current_user = get_jwt_identity()
    page = int(request.args.get("page")) - 1
    size = int(request.args.get("page_size"))
    network_id = request.args.get("network_id")
    questions = db.run(
        "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(question) set question.label = labels(question)[0] return question SKIP %s LIMIT %s"
        % (current_user, network_id, page * size, size)
    ).data()
    return jsonify(questions)


@start_controller.route("/resource/getAll", methods=["GET"])
@jwt_required
def resource_getall(db: Graph):
    current_user = get_jwt_identity()
    page = int(request.args.get("page")) - 1
    size = int(request.args.get("page_size"))
    network_id = request.args.get("network_id")
    questions = db.run(
        "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_RESOURCE]-(resource) set resource.label = labels(resource)[0] return resource SKIP %s LIMIT %s"
        % (current_user, network_id, page * size, size)
    ).data()
    return jsonify(questions)


@start_controller.route("/questions/get", methods=["GET"])
@jwt_required
def questions_get(db: Graph):
    current_user = get_jwt_identity()
    uuid = request.args.get("uuid")
    network_id = request.args.get("network_id")
    questions = db.run(
        "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(question{uuid: '%s'}) return question"
        % (current_user, network_id, uuid)
    ).data()

    return jsonify(questions)


@start_controller.route("/resources/get", methods=["GET"])
@jwt_required
def resources_get(db: Graph):
    current_user = get_jwt_identity()
    uuid = request.args.get("uuid")
    network_id = request.args.get("network_id")
    questions = db.run(
        "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_RESOURCE]-(resource{uuid: '%s'}) return resource"
        % (current_user, network_id, uuid)
    ).data()
    return jsonify(questions)


from .modules.controller import make_network, registerCourse
import re


@start_controller.route("/network/import", methods=["POST"])
@jwt_required
def import_network(db: Graph):
    current_user = get_jwt_identity()
    dataDict = request.get_json(force=True)

    url_base = dataDict["url_base"]
    token = dataDict["token"]
    course_name = dataDict["course_name"]

    result = getCourseByName(url_base, token, course_name)
    try:
        if "courses" in result and len(result["courses"]) > 0:
            # criar rede
            course_id = result["courses"][0]["id"]

            result_network = make_network(
                db, current_user, course_name, url_base, token, course_id
            )

            all_chats = getChatByCourse(url_base, token, course_id)
            all_databases = getDatabaseByCourse(url_base, token, course_id)
            all_lti = getltiByCourse(url_base, token, course_id)
            all_forums = getForumsByCourse(url_base, token, course_id)

            all_glossaries = getGlossariesByCourse(url_base, token, course_id)
            all_quizzes = getQuizzestByCourse(url_base, token, course_id)
            all_wikis = getWikisByCourse(url_base, token, course_id)

            bpmn_data = import_bpmn_activitys(all_quizzes)
            Network.update_by_user(
                db,
                current_user,
                result_network.id,
                bpmn_data,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            )

            # importar atividades
            for chat in all_chats["chats"]:

                description = re.sub("<[^<]+?>", "", chat["intro"])
                create_chat(
                    db,
                    current_user,
                    chat["name"],
                    description,
                    result_network.id,
                    chat["id"],
                    chat["course"],
                    url_base,
                    token,
                )

            for data in all_databases["databases"]:
                description = re.sub("<[^<]+?>", "", data["intro"])
                create_database(
                    db,
                    current_user,
                    data["name"],
                    description,
                    result_network.id,
                    data["id"],
                    data["course"],
                    url_base,
                    token,
                )

            for lti in all_lti["ltis"]:
                description = re.sub("<[^<]+?>", "", lti["intro"])
                create_lti(
                    db,
                    current_user,
                    lti["name"],
                    description,
                    result_network.id,
                    lti["id"],
                    lti["course"],
                    url_base,
                    token,
                )

            for forum in all_forums:
                description = re.sub("<[^<]+?>", "", forum["intro"])
                create_forum(
                    db,
                    current_user,
                    forum["name"],
                    description,
                    result_network.id,
                    forum["id"],
                    forum["course"],
                    url_base,
                    token,
                )

            for glossary in all_glossaries["glossaries"]:
                description = re.sub("<[^<]+?>", "", glossary["intro"])
                create_glossary(
                    db,
                    current_user,
                    glossary["name"],
                    description,
                    result_network.id,
                    glossary["id"],
                    glossary["course"],
                    url_base,
                    token,
                )

            for quiz in all_quizzes["quizzes"]:
                description = re.sub("<[^<]+?>", "", quiz["intro"])
                create_quiz(
                    db,
                    current_user,
                    quiz["name"],
                    description,
                    result_network.id,
                    quiz["id"],
                    quiz["course"],
                    url_base,
                    token,
                )

            for wiki in all_wikis["wikis"]:
                description = re.sub("<[^<]+?>", "", wiki["intro"])
                create_wiki(
                    db,
                    current_user,
                    wiki["name"],
                    description,
                    result_network.id,
                    wiki["id"],
                    wiki["course"],
                    url_base,
                    token,
                )

            registerCourse(
                db,
                course_id,
                result_network.id,
                current_user,
                result["courses"][0]["fullname"],
                result["courses"][0]["shortname"],
            )

            return jsonify({"message": "Rede importada"}), 200

        else:
            return jsonify({}), 404
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        return "error", 400


def import_bpmn_activitys(all_quizzes):

    quizzes = sorted(all_quizzes["quizzes"], key=lambda x: x["timeclose"], reverse=True)
    quizzes_group = []

    index_reference = -1
    for index, quiz in enumerate(quizzes):
        first_closetime_quiz_group = (
            quizzes_group[index_reference][0]["timeclose"]
            if index_reference != -1
            else -1
        )
        if index == 0 or quiz["timeopen"] > first_closetime_quiz_group:
            index_reference += 1
            quizzes_group.append([quiz])
        else:
            quizzes_group[index_reference].append(quiz)

    data_bpmn = """{"type":"custom:start","id":"custom:start_0","name":"Início","x":70,"y":30},"""
    x = 70
    y = 30
    global_activity_index = 1
    global_connection_index = 1
    for group_index, quizzes in enumerate(quizzes_group):
        x += 200
        y = 30 - (len(quizzes) * 80) / 2
        for index, quiz in enumerate(quizzes):
            data_bpmn += """
            {"type":"custom:atividadeBasica","id":"custom:atividadeBasica_%d","name":"Atividade %d","activity_count":%d,"x":%d,"y":%d},
            """ % (
                global_activity_index,
                global_activity_index,
                global_activity_index,
                x,
                y,
            )
            quiz["id"] = f"custom:atividadeBasica_{global_activity_index}"
            quiz["x"] = x
            quiz["y"] = y
            global_activity_index += 1
            y += 100

            if group_index == 0:
                data_bpmn += """{"type":"custom:connection","id":"custom:connection_%d",
                "waypoints":[{"x":110,"y":48},{"x":%d,"y":%d}],"source":"custom:start_0","target":"%s"},
                """ % (
                    global_connection_index,
                    x,
                    y - 82,
                    f"custom:atividadeBasica_{global_activity_index-1}",
                )
                global_connection_index += 1
            else:
                for item in quizzes_group[group_index - 1]:
                    data_bpmn += """{"type":"custom:connection","id":"custom:connection_%d",
                    "waypoints":[{"x":%d,"y":%d},{"x":%d,"y":%d}],"source":"%s","target":"%s"},
                    """ % (
                        global_connection_index,
                        item["x"],
                        item["y"],
                        x,
                        y - 82,
                        item["id"],
                        f"custom:atividadeBasica_{global_activity_index-1}",
                    )
                    global_connection_index += 1

    if len(quizzes_group) > 0:
        for item in quizzes_group[len(quizzes_group) - 1]:
            data_bpmn += """{"type":"custom:connection","id":"custom:connection_%d",
            "waypoints":[{"x":%d,"y":%d},{"x":%d,"y":%d}],"source":"%s","target":"custom:end_0"},
            """ % (
                global_connection_index,
                item["x"] + 30,
                item["y"] + 20,
                x + 200,
                48,
                item["id"],
            )
            global_connection_index += 1

    data_bpmn += """{"type":"custom:end","id":"custom:end_0","name":"Fim","x":%d,"y":%d}
    """ % (
        x + 200,
        30,
    )
    return """[%s]""" % data_bpmn


@start_controller.route("/courses/getall", methods=["GET"])
@jwt_required
def courses_getall(db: Graph):
    current_user = get_jwt_identity()
    page = int(request.args.get("page")) - 1
    size = int(request.args.get("page_size"))

    courses = db.run(
        "MATCH (p:User{email:'%s'})-[r1]-(a:Network)-[r:HAS_COURSE]-(course) \
        set course.label = labels(course)[0]\
        return course.id as id, course.fullname as fullname, course.shortname as shortname, course.network_id as network_id, course.created_at as created_at \
        ORDER BY course.created_at DESC SKIP %s LIMIT %s"
        % (current_user, page * size, size)
    ).data()

    return jsonify(courses)


@start_controller.route("/courses/get", methods=["GET"])
@jwt_required
def courses_get_by_id(db: Graph):
    current_user = get_jwt_identity()
    course_id = request.args.get("course_id")

    courses = db.run(
        "MATCH (p:User{email:'%s'})-[r1]-(a:Network)-[r:HAS_COURSE]-(course{id:%s}) \
        set course.label = labels(course)[0]\
        return course.id as id, course.fullname as fullname, course.shortname as shortname, course.network_id as network_id, course.created_at as created_at \
        "
        % (current_user, course_id)
    ).data()
    return jsonify(courses)


from app.modules.general.status import getStatus, getGradeStatus
from app.views import get_enrolled
from datetime import datetime


def getDateList():
    month = datetime.now().month
    year = datetime.now().year
    array_result = [f"{year}-{month}-01"]

    for i in range(1, 9):
        month = month - 1
        if month == 0:
            month = 12
            year = year - 1
        array_result.append(f"{year}-{month}-01")

    return array_result


@start_controller.route("/status/get", methods=["GET"])
@jwt_required
def get_status(db: Graph):
    current_user = get_jwt_identity()
    network_id = request.args.get("network_id")
    course_id = request.args.get("course_id")

    network = db.run(
        "MATCH (p:User{email:'%s'})-[r1]-(net:Network{id:'%s'}) return net"
        % (current_user, network_id)
    ).data()[0]["net"]

    users = get_enrolled(db, current_user, network_id, course_id)
    users = ",".join([str(user["id"]) for user in users])
    date_list = ",".join(getDateList())

    result = getStatus(network["url"], network["token"], course_id, users, date_list)

    return jsonify(result)


@start_controller.route("/grade_status/get", methods=["GET"])
@jwt_required
def get_grade_status(db: Graph):
    current_user = get_jwt_identity()
    network_id = request.args.get("network_id")
    course_id = request.args.get("course_id")

    network = db.run(
        "MATCH (p:User{email:'%s'})-[r1]-(net:Network{id:'%s'}) return net"
        % (current_user, network_id)
    ).data()[0]["net"]

    users = get_enrolled(db, current_user, network_id, course_id)
    users = ",".join([str(user["id"]) for user in users])

    result = getGradeStatus(network["url"], network["token"], course_id, users)

    return jsonify(result)


@start_controller.route("/general/status", methods=["GET"])
@jwt_required
def general_account_status(db: Graph):
    try:
        current_user = get_jwt_identity()
        activitys_query = (
            "MATCH (p:User{email:'%s'})-[r]-(activity)-[r2]-(course:Course)-[r3:HAS_INSTANCE]-(i) return COUNT(DISTINCT i) as total"
            % current_user
        )
        activitys_result = db.run(activitys_query).data()
        networks_result = Network.get_length(db, current_user)
        courses_result = Course.get_length(db, current_user)

        chat_query = (
            "MATCH (p:User{email:'%s'})-[r]-(activity)-[r2]-(course:Course)-[r3:HAS_INSTANCE]-(i:ChatInstance) return COUNT(DISTINCT i) as total"
            % current_user
        )
        quiz_query = (
            "MATCH (p:User{email:'%s'})-[r]-(activity)-[r2]-(course:Course)-[r3:HAS_INSTANCE]-(i:QuizInstance) return COUNT(DISTINCT i) as total"
            % current_user
        )
        choice_query = (
            "MATCH (p:User{email:'%s'})-[r]-(activity)-[r2]-(course:Course)-[r3:HAS_INSTANCE]-(i:ChoiceInstance) return COUNT(DISTINCT i) as total"
            % current_user
        )
        forum_query = (
            "MATCH (p:User{email:'%s'})-[r]-(activity)-[r2]-(course:Course)-[r3:HAS_INSTANCE]-(i:ForumInstance) return COUNT(DISTINCT i) as total"
            % current_user
        )

        list_courses = db.run(
            "MATCH (p:User{email:'%s'})-[r]-(net:Network)-[r2]-(course:Course) WHERE net.token <> '' return net.id, course.id"
            % current_user
        ).data()
        total_users = 0

        for item in list_courses:
            total_users += len(
                get_enrolled(db, current_user, item["net.id"], item["course.id"])
            )

        chat_result = db.run(chat_query).data()
        quiz_result = db.run(quiz_query).data()
        choice_result = db.run(choice_query).data()
        forum_result = db.run(forum_query).data()

        return jsonify(
            {
                "networks": networks_result[0]["total"],
                "courses": courses_result[0]["total"],
                "activitys": activitys_result[0]["total"],
                "users": total_users,
                "chat": chat_result[0]["total"],
                "quiz": quiz_result[0]["total"],
                "choice": choice_result[0]["total"],
                "forum": forum_result[0]["total"],
            }
        )

    except Exception as e:
        print(str(e), file=sys.stderr)


class ExternToolResource(Resource):
    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        search = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(externtool:ExternTool{uuid:'%s'}) return externtool"
            % (current_user, network_id, uuid)
        ).data()
        return jsonify(search)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        try:
            externtool = ExternTool()
            externtool.uuid = uuid
            externtool.label = "externtool"
            externtool.name = dataDict["name"]
            externtool.description = dataDict["description"]

            self.db.push(externtool)

            Network.addExternTool(self.db, current_user, dataDict["network_id"], uuid)

            network = self.db.run(
                "MATCH (p:User{email:'%s'})-[r1]-(net:Network{id:'%s'}) return net"
                % (current_user, dataDict["network_id"])
            ).data()[0]["net"]
            externtool = self.db.run(
                "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(externtool:ExternTool{uuid:'%s'}) return externtool"
                % (current_user, dataDict["network_id"], uuid)
            ).data()[0]["externtool"]

            if network and network["url"] != None:
                all_courses = self.db.run(
                    "MATCH (u:User{email:'%s'})-[r]-(a:Network{id:'%s'})-[:HAS_COURSE]-(course) return course"
                    % (current_user, dataDict["network_id"])
                ).data()
                for course in all_courses:
                    course = course["course"]
                    createQuestion(
                        externtool,
                        network["url"],
                        network["token"],
                        int(course["id"]),
                        self.db,
                        current_user,
                    )

            createLog(
                current_user,
                dataDict["network_id"],
                "Criou uma nova atividade: " + str(dataDict["name"]),
            )

        except Exception as e:
            print("ERRO:", file=sys.stderr)
            print(str(e), file=sys.stderr)

        return jsonify({"sucess": True})

    @jwt_required
    def put(self):

        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]
        name = dataDict["name"]
        description = dataDict["description"]

        activities = Network.getActivity(self.db, current_user, uuid, "ExternTool")

        if len(activities) > 0:
            activity = dict(activities[0]["activity"])

            query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(externtool:ExternTool{{uuid:'{uuid}'}}) \
            SET externtool.name = '{name}',\
            externtool.description = '{description}'\
                 return externtool"

            self.db.run(query).data()

            network = self.db.run(
                f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(network:Network{{id:'{network_id}'}}) return network"
            ).data()[0]["network"]

            all_instances = self.db.run(
                f"MATCH (instance:ExternToolInstance{{id_extern_tool: '{uuid}'}}) return instance"
            ).data()

            # atualizar todas 'turmas' já criadas
            for instance in all_instances:
                result = instance["instance"]
                updateExterntool(
                    network["url"],
                    network["token"],
                    result["id_instance"],
                    name,
                    description,
                )

            if activity["name"] == name:
                createLog(
                    current_user,
                    dataDict["network_id"],
                    "Atualizou a atividade: " + str(dataDict["name"]),
                )
            else:
                createLog(
                    current_user,
                    dataDict["network_id"],
                    f"Atualizou a atividade {activity['name']} para {name}",
                )

            return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(externtool:ExternTool{{uuid:'{uuid}'}}) DETACH DELETE externtool "
        self.db.run(query)

        return jsonify({"Deleted": True})


class ForumResource(Resource):
    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        forum = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(forum:Forum{uuid:'%s'}) return forum"
            % (current_user, network_id, uuid)
        ).data()
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
        forum.label = "forum"

        self.db.push(forum)

        Network.addForum(self.db, current_user, dataDict["network_id"], uuid)
        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )

        forum = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(forum:Forum{uuid:'%s'}) return forum"
            % (current_user, dataDict["network_id"], uuid)
        ).data()[0]["forum"]
        courses_already_created = self.db.run(
            "MATCH (p:User{email:'%s'})-[r]-(net:Network{id: '%s'})-[r2]-(course:Course) return course.id as id, net.url as url, net.token as token"
            % (current_user, dataDict["network_id"])
        ).data()
        for r in courses_already_created:
            createQuestion(forum, r["url"], r["token"], r["id"], self.db, current_user)

        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        try:
            dataDict = request.get_json(force=True)
            current_user = get_jwt_identity()

            network_id = dataDict["network_id"]
            uuid = dataDict["uuid"]
            name = dataDict["name"]
            description = dataDict["description"]

            activities = Network.getActivity(self.db, current_user, uuid, "Forum")

            if len(activities) > 0:
                activity = dict(activities[0]["activity"])

                query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(forum:Forum{{uuid:'{uuid}'}}) \
                SET forum.name = '{name}',\
                forum.description = '{description}'\
                return forum"

                self.db.run(query).data()

                network = self.db.run(
                    f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(network:Network{{id:'{network_id}'}}) return network"
                ).data()[0]["network"]

                all_instances = self.db.run(
                    f"MATCH (instance:ForumInstance{{id_forum: '{uuid}'}}) return instance"
                ).data()

                # atualizar todas 'turmas' já criadas
                for instance in all_instances:
                    result = instance["instance"]
                    updateForum(
                        network["url"],
                        network["token"],
                        result["id_instance"],
                        name,
                        description,
                    )

                if activity["name"] == name:
                    createLog(
                        current_user,
                        dataDict["network_id"],
                        "Atualizou a atividade: " + str(dataDict["name"]),
                    )
                else:
                    createLog(
                        current_user,
                        dataDict["network_id"],
                        f"Atualizou a atividade {activity['name']} para {name}",
                    )

                return jsonify({"updated": True})
        except Exception as e:
            print("??????????????????????????????", file=sys.stderr)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(n:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(forum:Forum{{uuid:'{uuid}'}}) DETACH DELETE forum "
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
        glossario = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(glossario:Glossario{uuid:'%s'}) return glossario"
            % (current_user, network_id, uuid)
        ).data()
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

        self.db.push(glossario)

        Network.addGlossario(self.db, current_user, dataDict["network_id"], uuid)
        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )
        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]
        name = dataDict["name"]
        description = dataDict["description"]

        activities = Network.getActivity(self.db, current_user, uuid, "Glossario")

        if len(activities) > 0:
            activity = dict(activities[0]["activity"])

            query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(glossario:Glossario{{uuid:'{uuid}'}}) \
            SET glossario.name = '{name}',\
            glossario.description = '{description}'\
                return glossario"

            self.db.run(query).data()

            network = self.db.run(
                f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(network:Network{{id:'{network_id}'}}) return network"
            ).data()[0]["network"]

            all_instances = self.db.run(
                f"MATCH (instance:GlossarioInstance{{id_glossario: '{uuid}'}}) return instance"
            ).data()

            # atualizar todas 'turmas' já criadas
            for instance in all_instances:
                result = instance["instance"]
                updateGlossario(
                    network["url"],
                    network["token"],
                    result["id_instance"],
                    name,
                    description,
                )

            if activity["name"] == name:
                createLog(
                    current_user,
                    dataDict["network_id"],
                    "Atualizou a atividade: " + str(dataDict["name"]),
                )
            else:
                createLog(
                    current_user,
                    dataDict["network_id"],
                    f"Atualizou a atividade {activity['name']} para {name}",
                )

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
        search = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(search:Search{uuid:'%s'}) return search"
            % (current_user, network_id, uuid)
        ).data()
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
        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )
        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        name = dataDict["name"]
        description = dataDict["description"]
        allow_responses_from = dataDict["allow_responses_from"]
        responses_from = dataDict["responses_from"]

        allow_responses_to = dataDict["allow_responses_to"]
        responses_to = dataDict["responses_to"]

        type_username_recorded = dataDict["type_username_recorded"]
        allow_mult_send = dataDict["allow_mult_send"]
        allow_notice_send = dataDict["allow_notice_send"]
        allow_automatic_numbering = dataDict["allow_automatic_numbering"]

        show_analyze = dataDict["show_analyze"]
        conclusion_message = dataDict["conclusion_message"]
        next_link = dataDict["next_link"]

        conclusion_type = dataDict["conclusion_type"]
        view_required = dataDict["view_required"]
        finished_sent = dataDict["finished_sent"]
        allow_conclusion_date = dataDict["allow_conclusion_date"]
        conclusion_date = dataDict["conclusion_date"]

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
        url = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_RESOURCE]-(url:URL{uuid:'%s'}) return url"
            % (current_user, network_id, uuid)
        ).data()
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
        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )

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
        page = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_RESOURCE]-(page:Page{uuid:'%s'}) return page"
            % (current_user, network_id, uuid)
        ).data()
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
        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )

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
                 return page"

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
        file = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_RESOURCE]-(file:File{uuid:'%s'}) return file"
            % (current_user, network_id, uuid)
        ).data()
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
        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )

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
            file.description = '{description}',\
            file.type_display = '{type_display}',\
            file.type_filter_content = '{type_filter_content}',\
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

        network_id = request.args.get("network_id")
        id_transiction = request.args.get("id_transiction")
        current_user = get_jwt_identity()

        condition = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_CONDITION]-(con:Condition{id_transiction:'%s'}) return con"
            % (current_user, network_id, id_transiction)
        ).data()
        return jsonify(condition)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        print(dataDict, file=sys.stderr)
        condition = Condition()
        condition.id_activity = dataDict["id_activity"]
        condition.id_transiction = dataDict["id_transiction"]
        condition.name_activity = dataDict["name_activity"]
        condition.data = str(dataDict["data"])

        self.db.push(condition)

        Network.addCondition(
            self.db, current_user, dataDict["network_id"], dataDict["id_transiction"]
        )
        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )

        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        network_id = dataDict["network_id"]

        id_transiction = dataDict["id_transiction"]

        name = dataDict["name_activity"]
        data = str(dataDict["data"])

        query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_CONDITION]-(condition:Condition{{id_transiction:'{id_transiction}'}}) \
            SET condition.name_activity = '{name}',\
            condition.data = '{data}' return condition"

        self.db.run(query).data()

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        id_transiction = dataDict["id_transiction"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_CONDITION]-(condition:Condition{{id_transiction:'{id_transiction}'}}) DETACH DELETE condition "
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
        quiz = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(quiz:Quiz{uuid:'%s'}) return quiz"
            % (current_user, network_id, uuid)
        ).data()
        return jsonify(quiz)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        quiz = Quiz()
        quiz.has_trigged = "False"
        quiz.uuid = uuid
        quiz.name = dataDict["name"]
        quiz.label = "quiz"
        quiz.description = dataDict["description"]

        self.db.push(quiz)

        Network.addQuiz(self.db, current_user, dataDict["network_id"], uuid)
        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )

        quiz = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(quiz:Quiz{uuid:'%s'}) return quiz"
            % (current_user, dataDict["network_id"], uuid)
        ).data()[0]["quiz"]
        courses_already_created = self.db.run(
            "MATCH (p:User{email:'%s'})-[r]-(net:Network{id: '%s'})-[r2]-(course:Course) return course.id as id, net.url as url, net.token as token"
            % (current_user, dataDict["network_id"])
        ).data()
        for r in courses_already_created:
            createQuestion(quiz, r["url"], r["token"], r["id"], self.db, current_user)

        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        try:
            dataDict = request.get_json(force=True)
            current_user = get_jwt_identity()

            network_id = dataDict["network_id"]
            uuid = dataDict["uuid"]
            name = dataDict["name"]
            description = dataDict["description"]

            activities = Network.getActivity(self.db, current_user, uuid, "Quiz")

            if len(activities) > 0:
                activity = dict(activities[0]["activity"])

                query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(quiz:Quiz{{uuid:'{uuid}'}}) \
                SET quiz.name = '{name}',\
                quiz.description = '{description}'\
                return quiz"

                self.db.run(query).data()

                network = self.db.run(
                    f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(network:Network{{id:'{network_id}'}}) return network"
                ).data()[0]["network"]

                all_instances = self.db.run(
                    f"MATCH (instance:QuizInstance{{id_quiz: '{uuid}'}}) return instance"
                ).data()

                # atualizar todas 'turmas' já criadas
                for instance in all_instances:
                    result = instance["instance"]
                    updateQuiz(
                        network["url"],
                        network["token"],
                        result["id_instance"],
                        name,
                        description,
                    )

                if activity["name"] == name:
                    createLog(
                        current_user,
                        dataDict["network_id"],
                        "Atualizou a atividade: " + str(dataDict["name"]),
                    )
                else:
                    createLog(
                        current_user,
                        dataDict["network_id"],
                        f"Atualizou a atividade {activity['name']} para {name}",
                    )
        except Exception as e:
            print("****************************", file=sys.stderr)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)

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


def create_chat(
    db,
    current_user,
    chat_name,
    chat_description,
    chat_network_id,
    id_chat=None,
    course_id=None,
    url_base=None,
    token=None,
):
    uuid = generateUUID()

    chat = Chat()
    chat.uuid = uuid
    chat.label = "chat"
    chat.name = chat_name
    chat.description = chat_description
    db.push(chat)

    Network.addChat(db, current_user, chat_network_id, uuid)

    if id_chat != None:
        group = createGroup(
            url_base,
            token,
            course_id,
            str(chat_name) + str(generateUUID()),
            "Caminho de aprendizado",
        )[0]

        chat_instance = ChatInstance()
        chat_instance.uuid = generateUUID()
        chat_instance.id_chat = uuid
        chat_instance.id_group = group["id"]
        chat_instance.id_instance = id_chat

        db.push(chat_instance)

        Course.addChat(db, current_user, course_id, chat_instance.uuid)

        setChatGroup(url_base, token, id_chat, course_id, group["id"])

    return uuid


def create_glossary(
    db,
    current_user,
    glossary_name,
    glossary_description,
    glossary_network_id,
    id_glossary=None,
    course_id=None,
    url_base=None,
    token=None,
):
    uuid = generateUUID()

    glossary = Glossario()
    glossary.uuid = uuid
    glossary.label = "glossary"
    glossary.name = glossary_name
    glossary.description = glossary_description
    db.push(glossary)

    Network.addGlossario(db, current_user, glossary_network_id, uuid)

    if id_glossary != None:
        group = createGroup(
            url_base,
            token,
            course_id,
            str(glossary_name) + str(generateUUID()),
            "Caminho de aprendizado",
        )[0]

        glossary_instance = GlossarioInstance()
        glossary_instance.uuid = generateUUID()
        glossary_instance.id_glossary = uuid
        glossary_instance.id_group = group["id"]
        glossary_instance.id_instance = id_glossary

        db.push(glossary_instance)

        Course.addGlossario(db, current_user, course_id, glossary_instance.uuid)

        setGlossaryGroup(url_base, token, id_glossary, course_id, group["id"])


def create_quiz(
    db,
    current_user,
    quiz_name,
    quiz_description,
    quiz_network_id,
    id_quiz=None,
    course_id=None,
    url_base=None,
    token=None,
):
    uuid = generateUUID()

    quiz = Quiz()
    quiz.uuid = uuid
    quiz.has_trigged = "False"
    quiz.label = "quiz"
    quiz.name = quiz_name
    quiz.description = quiz_description
    db.push(quiz)

    Network.addQuiz(db, current_user, quiz_network_id, uuid)

    if id_quiz != None:
        group = createGroup(
            url_base,
            token,
            course_id,
            str(quiz_name) + str(generateUUID()),
            "Caminho de aprendizado",
        )[0]

        quiz_instance = QuizInstance()
        quiz_instance.uuid = generateUUID()
        quiz_instance.id_quiz = uuid
        quiz_instance.id_group = group["id"]
        quiz_instance.id_instance = id_quiz

        db.push(quiz_instance)

        Course.addQuiz(db, current_user, course_id, quiz_instance.uuid)

        setQuizGroup(url_base, token, id_quiz, course_id, group["id"])


def create_forum(
    db,
    current_user,
    forum_name,
    forum_description,
    forum_network_id,
    id_forum=None,
    course_id=None,
    url_base=None,
    token=None,
):
    uuid = generateUUID()

    forum = Forum()
    forum.uuid = uuid
    forum.label = "forum"
    forum.name = forum_name
    forum.description = forum_description
    db.push(forum)

    Network.addForum(db, current_user, forum_network_id, uuid)

    if id_forum != None:
        group = createGroup(
            url_base,
            token,
            course_id,
            str(forum_name) + str(generateUUID()),
            "Caminho de aprendizado",
        )[0]

        forum_instance = ForumInstance()
        forum_instance.uuid = generateUUID()
        forum_instance.id_forum = uuid
        forum_instance.id_group = group["id"]
        forum_instance.id_instance = id_forum

        db.push(forum_instance)

        Course.addForum(db, current_user, course_id, forum_instance.uuid)

        setForumGroup(url_base, token, id_forum, course_id, group["id"])


def create_lti(
    db,
    current_user,
    lti_name,
    lti_description,
    lti_network_id,
    id_lti=None,
    course_id=None,
    url_base=None,
    token=None,
):
    uuid = generateUUID()

    lti = ExternTool()
    lti.uuid = uuid
    lti.label = "lti"
    lti.name = lti_name
    lti.description = lti_description
    db.push(lti)

    Network.addExternTool(db, current_user, lti_network_id, uuid)

    if id_lti != None:
        group = createGroup(
            url_base,
            token,
            course_id,
            str(lti_name) + str(generateUUID()),
            "Caminho de aprendizado",
        )[0]

        lti_instance = ExternToolInstance()
        lti_instance.uuid = generateUUID()
        lti_instance.id_lti = uuid
        lti_instance.id_group = group["id"]
        lti_instance.id_instance = id_lti

        db.push(lti_instance)

        Course.addExternTool(db, current_user, course_id, lti_instance.uuid)

        setLTIGroup(url_base, token, id_lti, course_id, group["id"])


def create_database(
    db,
    current_user,
    data_name,
    data_description,
    data_network_id,
    id_data=None,
    course_id=None,
    url_base=None,
    token=None,
):
    uuid = generateUUID()

    data = Database()
    data.uuid = uuid
    data.label = "data"
    data.name = data_name
    data.description = data_description
    db.push(data)

    Network.addDatabase(db, current_user, data_network_id, uuid)

    if id_data != None:
        group = createGroup(
            url_base,
            token,
            course_id,
            str(data_name) + str(generateUUID()),
            "Caminho de aprendizado",
        )[0]

        data_instance = DatabaseInstance()
        data_instance.uuid = generateUUID()
        data_instance.id_database = uuid
        data_instance.id_group = group["id"]
        data_instance.id_instance = id_data

        db.push(data_instance)

        Course.addDatabase(db, current_user, course_id, data_instance.uuid)

        setDatabaseGroup(url_base, token, id_data, course_id, group["id"])


def create_wiki(
    db,
    current_user,
    wiki_name,
    wiki_description,
    wiki_network_id,
    id_wiki=None,
    course_id=None,
    url_base=None,
    token=None,
):
    uuid = generateUUID()

    wiki = Wiki()
    wiki.uuid = uuid
    wiki.label = "wiki"
    wiki.name = wiki_name
    wiki.description = wiki_description
    db.push(wiki)

    Network.addWiki(db, current_user, wiki_network_id, uuid)

    if id_wiki != None:
        group = createGroup(
            url_base,
            token,
            course_id,
            str(wiki_name) + str(generateUUID()),
            "Caminho de aprendizado",
        )[0]

        wiki_instance = WikiInstance()
        wiki_instance.uuid = generateUUID()
        wiki_instance.id_wiki = uuid
        wiki_instance.id_group = group["id"]
        wiki_instance.id_instance = id_wiki

        db.push(wiki_instance)

        Course.addWiki(db, current_user, course_id, wiki_instance.uuid)

        setWikiGroup(url_base, token, id_wiki, course_id, group["id"])


class ChatResource(Resource):
    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        chat = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(chat:Chat{uuid:'%s'}) return chat"
            % (current_user, network_id, uuid)
        ).data()
        return jsonify(chat)

    @jwt_required
    def post(self):

        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        uuid = create_chat(
            self.db,
            current_user,
            dataDict["name"],
            dataDict["description"],
            dataDict["network_id"],
        )

        network = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(net:Network{id:'%s'}) return net"
            % (current_user, dataDict["network_id"])
        ).data()[0]["net"]
        chat = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(chat:Chat{uuid:'%s'}) return chat"
            % (current_user, dataDict["network_id"], uuid)
        ).data()[0]["chat"]

        if network and network["url"] != None:

            all_courses = self.db.run(
                "MATCH (u:User{email:'%s'})-[r]-(a:Network{id:'%s'})-[:HAS_COURSE]-(course) return course"
                % (current_user, dataDict["network_id"])
            ).data()

            for course in all_courses:
                course = course["course"]
                createQuestion(
                    chat,
                    network["url"],
                    network["token"],
                    int(course["id"]),
                    self.db,
                    current_user,
                )

        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )

        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        try:
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

            chat = self.db.run(
                "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(chat:Chat{uuid:'%s'}) return chat"
                % (current_user, network_id, uuid)
            ).data()
            network = self.db.run(
                "MATCH (p:User{email:'%s'})-[r1]-(network:Network{id:'%s'}) return network"
                % (current_user, network_id)
            ).data()[0]["network"]

            uuid_chat = chat[0]["chat"]["uuid"]

            all_instances = self.db.run(
                "MATCH (instance:ChatInstance{id_chat: '%s'}) return instance"
                % (uuid_chat)
            ).data()

            # atualizar todas 'turmas' já criadas
            for instance in all_instances:
                result = instance["instance"]
                updateChat(
                    network["url"],
                    network["token"],
                    result["id_instance"],
                    name,
                    description,
                )

            return jsonify({"updated": True})
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(chat:Chat{{uuid:'{uuid}'}}) DETACH DELETE chat "
        self.db.run(query)

        return jsonify({"Deleted": True})


class WikiResource(Resource):
    def __init__(self, database):
        # database is a dependency
        self.db = database

    @jwt_required
    def get(self):
        uuid = request.args.get("uuid")
        network_id = request.args.get("network_id")
        current_user = get_jwt_identity()
        wiki = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(wiki:Wiki{uuid:'%s'}) return wiki"
            % (current_user, network_id, uuid)
        ).data()
        return jsonify(wiki)

    @jwt_required
    def post(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()
        uuid = generateUUID()

        wiki = Wiki()
        wiki.uuid = uuid
        wiki.name = dataDict["name"]
        wiki.description = dataDict["description"]

        self.db.push(wiki)

        Network.addWiki(self.db, current_user, dataDict["network_id"], uuid)
        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )

        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]
        name = dataDict["name"]
        description = dataDict["description"]

        activities = Network.getActivity(self.db, current_user, uuid, "Wiki")

        if len(activities) > 0:
            activity = dict(activities[0]["activity"])

            query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(wiki:Wiki{{uuid:'{uuid}'}}) \
            SET wiki.name = '{name}',\
            wiki.description = '{description}'\
            return wiki"

            self.db.run(query).data()

            network = self.db.run(
                f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(network:Network{{id:'{network_id}'}}) return network"
            ).data()[0]["network"]

            all_instances = self.db.run(
                f"MATCH (instance:WikiInstance{{id_wiki: '{uuid}'}}) return instance"
            ).data()

            # atualizar todas 'turmas' já criadas
            for instance in all_instances:
                result = instance["instance"]
                updateWiki(
                    network["url"],
                    network["token"],
                    result["id_instance"],
                    name,
                    description,
                )

            if activity["name"] == name:
                createLog(
                    current_user,
                    dataDict["network_id"],
                    "Atualizou a atividade: " + str(dataDict["name"]),
                )
            else:
                createLog(
                    current_user,
                    dataDict["network_id"],
                    f"Atualizou a atividade {activity['name']} para {name}",
                )

        return jsonify({"updated": True})

    @jwt_required
    def delete(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]

        query = f"Match (p:User{{email:'{current_user}'}})-[r1]-(activity:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(wiki:Wiki{{uuid:'{uuid}'}}) DETACH DELETE wiki "
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
        lesson = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(lesson:Lesson{uuid:'%s'}) return lesson"
            % (current_user, network_id, uuid)
        ).data()
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
        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )

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
        database = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(database:Database{uuid:'%s'}) return database"
            % (current_user, network_id, uuid)
        ).data()
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

        """database.approval_required = dataDict["approval_required"]
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
        database.allow_end_date = dataDict["allow_end_date"]"""

        self.db.push(database)

        Network.addDatabase(self.db, current_user, dataDict["network_id"], uuid)
        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )

        database = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(database:Database{uuid:'%s'}) return database"
            % (current_user, dataDict["network_id"], uuid)
        ).data()[0]["database"]
        courses_already_created = self.db.run(
            "MATCH (p:User{email:'%s'})-[r]-(net:Network{id: '%s'})-[r2]-(course:Course) return course.id as id, net.url as url, net.token as token"
            % (current_user, dataDict["network_id"])
        ).data()
        for r in courses_already_created:
            createQuestion(
                database, r["url"], r["token"], r["id"], self.db, current_user
            )

        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]
        name = dataDict["name"]
        description = dataDict["description"]

        activities = Network.getActivity(self.db, current_user, uuid, "Database")

        if len(activities) > 0:
            activity = dict(activities[0]["activity"])

            query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(database:Database{{uuid:'{uuid}'}}) \
                SET database.name = '{name}',\
                database.description = '{description}'\
                return database"

            self.db.run(query).data()

            network = self.db.run(
                f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(network:Network{{id:'{network_id}'}}) return network"
            ).data()[0]["network"]

            all_instances = self.db.run(
                f"MATCH (instance:DatabaseInstance{{id_database: '{uuid}'}}) return instance"
            ).data()

            # atualizar todas 'turmas' já criadas
            for instance in all_instances:
                result = instance["instance"]
                updateDatabase(
                    network["url"],
                    network["token"],
                    result["id_instance"],
                    name,
                    description,
                )

            if activity["name"] == name:
                createLog(
                    current_user,
                    dataDict["network_id"],
                    "Atualizou a atividade: " + str(dataDict["name"]),
                )
            else:
                createLog(
                    current_user,
                    dataDict["network_id"],
                    f"Atualizou a atividade {activity['name']} para {name}",
                )

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
        choice = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(choice:Choice{uuid:'%s'}) return choice"
            % (current_user, network_id, uuid)
        ).data()
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

        self.db.push(choice)

        Network.addChoice(self.db, current_user, dataDict["network_id"], uuid)
        createLog(
            current_user,
            dataDict["network_id"],
            "Criou uma nova atividade: " + str(dataDict["name"]),
        )

        choice = self.db.run(
            "MATCH (p:User{email:'%s'})-[r1]-(a:Network{id:'%s'})-[r:HAS_QUESTIONS]-(choice:Choice{uuid:'%s'}) return choice"
            % (current_user, dataDict["network_id"], uuid)
        ).data()[0]["choice"]
        courses_already_created = self.db.run(
            "MATCH (p:User{email:'%s'})-[r]-(net:Network{id: '%s'})-[r2]-(course:Course) return course.id as id, net.url as url, net.token as token"
            % (current_user, dataDict["network_id"])
        ).data()
        for r in courses_already_created:
            createQuestion(choice, r["url"], r["token"], r["id"], self.db, current_user)

        return jsonify({"sucess": True})

    @jwt_required
    def put(self):
        dataDict = request.get_json(force=True)
        current_user = get_jwt_identity()

        network_id = dataDict["network_id"]
        uuid = dataDict["uuid"]
        name = dataDict["name"]
        description = dataDict["description"]

        activities = Network.getActivity(self.db, current_user, uuid, "Choice")

        if len(activities) > 0:
            activity = dict(activities[0]["activity"])

            query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(a:Network{{id:'{network_id}'}})-[r:HAS_QUESTIONS]-(choice:Choice{{uuid:'{uuid}'}}) \
            SET choice.name = '{name}',\
            choice.description = '{description}'\
            return choice"

            self.db.run(query).data()

            if activity["name"] == name:
                createLog(
                    current_user,
                    dataDict["network_id"],
                    "Atualizou a atividade: " + name,
                )
            else:
                createLog(
                    current_user,
                    dataDict["network_id"],
                    f"Atualizou a atividade {activity['name']} para {name}",
                )

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