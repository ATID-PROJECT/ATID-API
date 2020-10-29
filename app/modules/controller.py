from app.modules.general.course import get_enrolled, getUsersByCourse
from app.logManager import createLog

import sys
import hashlib
import json
from dynaconf import settings
from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from .UserObject import UserObject

from py2neo import Graph
import datetime
from . import account_controller
from flask import Response
from app.models import *

import random
import string
from py2neo import Relationship, Node
from .events.util import getGroupUsers, getPrevNodes

from .updateActivitys import updateFromMoodle
from urllib import parse
from .events import *
import os
from .activitys import *

#sys.path.append("..")
from app.JWTManager import jwt
import uuid 

import urllib.request, json 
import requests

from app.sqlite_models import *
from app.database import sqlite_db

source_moodle = "localhost"
url_moodle = "webservice/rest/server.php?wstoken={0}&wsfunction={1}&moodlewsrestformat=json"

def getUrl( complet_url ):
    url_parts = parse.urlparse( complet_url )
    return f"{url_parts.scheme}://{url_parts.netloc}"


def getCurrentDate():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def TimestampMillisec64():
    return int((datetime.datetime.utcnow() - datetime.datetime(1970, 1, 1)).total_seconds() * 1000)

def saveConnection( db, network_id, current_user, url, token ):
    query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(net:Network{{id:'{network_id}'}}) \
            SET net.url = '{getUrl(url)}',\
                net.token = '{token}'\
                return net"
 
    db.run(query)

def registerCourse( db, current_id, network_id, current_user, fullname, shortname ):
    
    course = Course()
    course.id = current_id
    course.fullname = fullname
    course.shortname = shortname
    course.network_id = network_id

    course.created_at = TimestampMillisec64()

    db.push(course)

    Network.addCourse(db, current_user, network_id, current_id)
    

def createCourse(url_base, token, fullname, shortname, db, network_id, current_user):
    function = "core_course_create_courses"
    
    params = f"&courses[0][fullname]={fullname}\
        &courses[0][shortname]={shortname}\
            &courses[0][categoryid]=1"
    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))
    r = requests.post( final_url, data={})
    result = r.json()

    registerCourse(db, result[0]['id'], network_id, current_user, fullname, shortname)

    return result[0]

def createGroup( url_base, token, course_id, name, description ):
    function = "core_group_create_groups"

    params = f"&groups[0][name]={name}&groups[0][description]={description}&groups[0][courseid]={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def createQuestion(item, url_base, token, course_id, db = None, current_user=""):
    try:
        label = str(item['label']).lower()
    
        if label == "chat":
            
            group = createGroup( url_base, token, course_id, item['name']+generateUUID(), "Caminho de aprendizado" )[0]
            
            chat =  createChat( url_base, token, course_id, item['name'], item['description'], group['id'] )
            
            chat_instance = ChatInstance()
            chat_instance.uuid = generateUUID()
            chat_instance.id_chat = item['uuid']
            chat_instance.id_group = group['id']
            chat_instance.id_instance = chat['id']

            db.push( chat_instance )

            Course.addChat(db, current_user, course_id, chat_instance.uuid)

        elif label == "database":
            group = createGroup( url_base, token, course_id, item['name']+generateUUID(), "Caminho de aprendizado" )[0]

            data = createDatabase( url_base, token, course_id, item['name'], item['description'], group['id'] )
            data_instance = DatabaseInstance()
            data_instance.uuid = generateUUID()
            data_instance.id_database = item['uuid']
            data_instance.id_instance = data['id']
            data_instance.id_group = group['id']

            db.push( data_instance )

            Course.addDatabase(db, current_user, course_id, data_instance.uuid)

        elif label == "forum":
            group = createGroup( url_base, token, course_id, item['name']+generateUUID(), "Caminho de aprendizado" )[0]
            forum = createForum( url_base, token, course_id, item['name'], item['description'], group['id'] )

            forum_instance = ForumInstance()
            forum_instance.uuid = generateUUID()
            forum_instance.id_forum = item['uuid']
            forum_instance.id_instance = forum['id']
            forum_instance.id_group = group['id']
            
            db.push( forum_instance )
            Course.addForum(db, current_user, course_id, forum_instance.uuid)

        elif label == "externtool":
            
            group = createGroup( url_base, token, course_id, item['name']+generateUUID(), "Caminho de aprendizado" )[0]
            lti = createExterntool( url_base, token, course_id, item['name'], item['description'], group['id'])
            
            lti_instance = ExternToolInstance()
            lti_instance.uuid = generateUUID()
            
            lti_instance.id_extern_tool = item['uuid']
            lti_instance.id_instance = lti['id']
            lti_instance.id_group = group['id']
            
            db.push( lti_instance )

            Course.addExternTool(db, current_user, course_id, lti_instance.uuid)

        elif label == "glossario":
            group = createGroup( url_base, token, course_id, item['name']+generateUUID(), "Caminho de aprendizado" )[0]

            glossario = createGlossario( url_base, token, course_id, item['name'], item['description'], group['id'] )
            
            glossario_instance = GlossarioInstance()
            glossario_instance.uuid = generateUUID()

            glossario_instance.id_group = group['id']
            glossario_instance.id_glossario = item['uuid']
            glossario_instance.id_instance = glossario['id']
            
            db.push( glossario_instance )

            Course.addGlossario(db, current_user, course_id, glossario_instance.uuid)
            

        elif label == "wiki":
            group = createGroup( url_base, token, course_id, item['name']+generateUUID(), "Caminho de aprendizado" )[0]
            wiki = createWiki( url_base, token, course_id, item['name'], item['description'], group['id'])
    
            wiki_instance = WikiInstance()
            wiki_instance.uuid = generateUUID()
            wiki_instance.id_wiki = item['uuid']
            wiki_instance.id_group = group['id']
            wiki_instance.id_instance = wiki['id']

            db.push( wiki_instance )

            Course.addWiki(db, current_user, course_id, wiki_instance.uuid)

        elif label == "choice":
            group = createGroup( url_base, token, course_id, item['name']+generateUUID(), "Caminho de aprendizado" )[0]
            choice = createChoice( url_base, token, course_id, item['name'], item['description'], group['id'] )

            choice_instance = ChoiceInstance()
            choice_instance.uuid = generateUUID()
            choice_instance.id_extern_tool = item['uuid']
            choice_instance.id_instance = choice['id']
            choice_instance.id_group = group['id']

            db.push( choice_instance )

            Course.addChoice(db, current_user, course_id, choice_instance.uuid)

        elif label == "quiz":
            group = createGroup( url_base, token, course_id, item['name']+generateUUID(), "Caminho de aprendizado" )[0]
            quiz = createQuiz( url_base, token, course_id, item['name'], item['description'], group['id'] )

            quiz_instance = QuizInstance()
            quiz_instance.uuid = generateUUID()
            quiz_instance.id_quiz = item['uuid']
            quiz_instance.id_group = group['id']
            quiz_instance.id_instance = quiz['id']
            
            db.push( quiz_instance )

            Course.addQuiz(db, current_user, course_id, quiz_instance.uuid)

        #elif label == "assign":
            #return createAssign(token, course_id, item['name'], item['description'] )
    except Exception as e:
        print('error===========================', file=sys.stderr)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)


@account_controller.route('/moodle/new_course', methods=['POST'])
@jwt_required
def makeCourse(db: Graph):
    current_user = get_jwt_identity()
    dataDict = request.get_json(force=True)

    network_id = dataDict["network_id"]
    fullname = dataDict["fullname"]
    shortname = dataDict["shortname"]
    
    create_course(db, current_user, network_id, fullname, shortname)
    
    return jsonify({"message": "curso criado com sucesso", "status": 200}), 200

def create_course(db, current_user, network_id, fullname, shortname):
    try:
        network = db.run("MATCH (p:User{email:'%s'})-[r1]-(net:Network{id:'%s'}) return net" % (current_user, network_id)).data()[0]['net']
        all_questions = db.run("MATCH (p:User{email:'%s'})-[r1]-(net:Network{id:'%s'})-[r2:HAS_QUESTIONS]-(q) return q" % (current_user, network_id)).data()

        result = createCourse(network['url'], network['token'], fullname, shortname, db, network_id, current_user)
        id_course = result['id']
        
        for question in all_questions:
            item = dict(question['q'])
            createQuestion( item, network['url'] , network['token'], int(id_course), db, current_user)

    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)
        print( "================" , file=sys.stderr)

def isDiffAddress(url_1, url_2):
    url1 = parse.urlparse(url_1)
    url2 = parse.urlparse(url_2)

    if url1.netloc != url2.netloc and len(url2.netloc) > 0:
        return True

    return False

@account_controller.route('/moodle/events/chat/', methods=['GET','POST','PUT'])
def eventChat(db: Graph):
    if request.method == "PUT":

        id_chat = request.form['id_chat']
        id_user = request.form['id_user']
        id_course = request.form['id_course']
        url_item = request.form['url_item']

        if isDiffAddress( url_item, request.remote_addr):
            abort(404)

        userCompletChat(db, id_course, id_chat, id_user, url_item)

        return ""
        
@account_controller.route('/moodle/events/quiz/', methods=['GET','POST','PUT'])
def eventQuiz(db: Graph):
    if request.method == "PUT":

        id_quiz = request.form['id_quiz']
        id_user = request.form['id_user']
        id_course = request.form['id_course']
        url_item = request.form['url_item']

        """
        verificar se o ip da emissor da mensagem é o mesmo o qual o servidor está hospedado
        """
        if isDiffAddress( url_item, request.remote_addr):
            abort(404)
        
        try:
            userCompletQuiz(db, id_course, id_quiz, id_user, url_item)
            
            return "ok"
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)
            return 400
            
@account_controller.route('/moodle/events/enrolment/', methods=['GET','POST','PUT'])
def eventEnrolment(db: Graph):
    if request.method == "PUT":

        id_user = request.form['id_user']
        id_course = request.form['id_course']
        url_host = request.form['url_item']

        try:
            UserToStart(db, url_host, id_course, id_user)
            return "ok", 200
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)
            return 400
    return "not found"
    
@account_controller.route('/moodle/update/', methods=['GET','POST','PUT'])
def updateQuestion(db: Graph):

    if request.method == "PUT":
        
        try:
            url_parts = parse.urlparse(request.form['url_item'])

            type_item = request.form['type_item']
            id_item = request.form['id_item']
            url_item = f"{url_parts.scheme}://{url_parts.netloc}"
            id_course = request.form['id_course']

            updateFromMoodle( db, type_item, url_item, id_course, id_item)

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)
            return 400
    return ""

def get_user( url, token, id ):
    function = "core_user_get_users_by_field"

    print( f"{url}/{url_moodle.format( token, function)}&field=id&values[0]={id}", file=sys.stderr )
    with urllib.request.urlopen(\
        f"{url}/{url_moodle.format( token, function)}&field=id&values[0]={id}" ) as url:
        data = json.loads(url.read().decode())

        if 'exception' in data:
            return None

        return {
            'username': data[0]['username'],
            'firstname': data[0]['firstname'],
            'fullname': data[0]['fullname'],
            'email': data[0]['email'],
            'profileimageurl': data[0]['profileimageurl'],
        }

from app.database import db

def quiz_dates():
    try:
        not_trigged = db.run("""
        MATCH (q:Quiz)
        RETURN q
        """).data()
        
        for nt in not_trigged:
            trigger = nt['q']
        
            db.run("""
            MATCH (q:Quiz)
            WHERE q.uuid = '{}'
            SET q.has_trigged = 'True'
            RETURN q
            """.format(trigger['uuid']))

            if 'open_date' in trigger and datetime.datetime.strptime( trigger['open_date'], '%Y-%m-%d %H:%M:%S') <= datetime.datetime.now()\
                and 'allow_open_date' in trigger and trigger['allow_open_date'] == 'True':
                network = db.run("MATCH (n:Network)-[]-(:Quiz{{uuid: '{0}' }}) RETURN n".format(trigger['uuid']) ).data()[0]['n']
                quiz_instance = db.run("MATCH (qi:QuizInstance) WHERE qi.id_quiz = '{0}' RETURN qi".format(trigger['uuid'])).data()[0]['qi']
                courses = db.run( "MATCH (n:Network)-[]-(c:Course) WHERE n.id = '{0}' RETURN c".format(network['id']) ).data()

                for c in courses:
                    course = c['c']
                    
                    old_nodes = getPrevNodes( db, trigger['uuid'], network, 'quiz')
                    for suggestion in old_nodes:
                        node1 = db.run("MATCH (qi:QuizInstance) WHERE qi.id_quiz = '{0}' RETURN qi".format(suggestion)).data()
                        node2 = db.run("MATCH (qi:ChatInstance) WHERE qi.id_chat = '{0}' RETURN qi".format(suggestion)).data()

                        node = None
                        if node1 != None and len(node1) > 0:
                            node = node1[0]['qi']
                        else:
                            node = node2[0]['qi']
                        users = getGroupUsers( network['url'], network['token'], int( node['id_group']  ))

                        if users != None:
                            for user_id in users:
                                eventOpenQuiz(db, int( course['id'] ), int(quiz_instance['id_instance']), int(user_id), network['url'])

                    #suggestion_uuid
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)
        return 400

@account_controller.route('/moodle/students/') 
@jwt_required
def getStudents(db: Graph):
    function = "core_group_get_group_members"
    current_user = get_jwt_identity()
    all_users = []

    network_id = request.args.get("network_id")
    activity_id = request.args.get("activity_id")
    activity_type = request.args.get("activity_type")
    course_id = request.args.get("course_id")

    type_lower = activity_type.lower()
    type_capitalize = activity_type.capitalize()

    if activity_type == "custom:start":
        result = get_enrolled(db, current_user, network_id)
        return jsonify( result )

    result = db.run(f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(net:Network{{id:'{network_id}'}}) return net").data()
    activity = db.run(f"MATCH (course:Course{{id:{course_id}}})-[r1]-(activity:{type_capitalize}Instance{{id_{type_lower}:'{activity_id}'}}) return activity").data()
    
    if len(activity)==0 or len(result)==0:
        return jsonify({"message": "", "status": 400}), 400
    else:
        result = result[0]['net']
        activity = activity[0]['activity']

    with urllib.request.urlopen(\
        f"{result['url']}/{url_moodle.format( result['token'] , function)}&groupids[0]={activity['id_group']}" ) as url:
        data = json.loads(url.read().decode())

        if 'exception' in data:
            return jsonify({"message": "`url` e `token` inválidos.", "status": 400}), 400
        
        for user_id in data[0]['userids']:

            user = get_user(result['url'],result['token'], user_id)
            if user:
                all_users.append( user )
    
    return jsonify(all_users), 200

@account_controller.route('/moodle/test', methods=['GET'])
@jwt_required
def moodleTest(db: Graph):
    function = "core_webservice_get_site_info"
    current_user = get_jwt_identity()

    url_base = request.args.get("url")
    network_id = request.args.get("network_id")
    token = request.args.get("token")
    print(str( url_base + "/" +(url_moodle.format(token, function))), file=sys.stderr)
    with urllib.request.urlopen(str( url_base + "/" +(url_moodle.format(token, function)))) as url:
        data = json.loads(url.read().decode())
        if 'exception' in data:
            return jsonify({"message": "`url` e `token` inválidos.", "status": 400}), 400

        saveConnection( db, network_id, current_user, url_base, token)
        return jsonify({"message": "`url` e `token` são obrigatórios.", "status": 200}), 200

    return jsonify({"message": "`url` e `token` são obrigatórios.", "status": 400}), 400

@account_controller.route('/moodle/get', methods=['GET'])
@jwt_required
def getFunctionMoodle():
    function = request.args.get("function")
    #change default token to owener token
    token = "dabfde815d37f639e32db61f420ad46c"

    with urllib.request.urlopen(str(source_moodle+(url_moodle.format(token, function)))) as url:
        data = json.loads(url.read().decode())
        return json.dumps(data)
    return jsonify({"error": "`function` são obrigatórios."}), 400

def getHash512(text):
    return hashlib.sha512(str(text).encode("UTF-8")).hexdigest()

def make_error(status_code, sub_code, message, action):
    response = jsonify({
        'status': status_code,
        'sub_code': sub_code,
        'message': message,
        'action': action
    })
    response.status_code = status_code
    return response

@account_controller.route("/users/isowner", methods=['GET'])
@jwt_required
def isOwnerNetwork(db: Graph):
    current_user = get_jwt_identity()

    result = User.fetch_network(db, current_user, request.args.get("network"))

    if len(result) > 0:
        return jsonify({'message': "ok"}),200
    else:
        return jsonify({"error": "operação não permitida"}),400

@account_controller.route('/users/share', methods=['GET','POST','DELETE'])
@jwt_required
def shareNetwork(db: Graph):
    current_user = get_jwt_identity()

    if request.method == "GET":
        result = User.fetch_network(db, current_user, request.args.get("network"))

        if( len(result) == 0):
            return jsonify({"error": "operação não permitida"}),400

        users_sharing = User.sharingNetworkAccess(db, request.args.get("network"))
        return jsonify( users_sharing )

    dataDict = json.loads(request.data)
    result = User.fetch_network(db, current_user, dataDict["network"])

    if( len(result) == 0):
        return jsonify({"error": "operação não permitida"}),400

    if request.method == "POST":
        
        target_user = User.secure_fetch_by_email(db, dataDict['email'])
        
        alredy_added = User.fetchSharedUser(db, dataDict['email'], dataDict['network'])
        if len(alredy_added) > 0:
            return jsonify({'error': "usuário já adicionado."}),400

        if len(target_user)!=0 and target_user[0]['user']['email'] != current_user:
            User.addNetworkShared(db, dataDict['email'], dataDict['network'])
            return jsonify({'message': "Usuário adicionado."}),200
        else:
            return jsonify({'error': "email inválido."}),400

    if request.method == "DELETE":
        User.unshare( db, dataDict["email"], dataDict['network'])

        return jsonify({'message': "Usuário removido."}),200

    return jsonify({'error': "Email é obrigatório"}),400

@account_controller.route('/users/activity/subnetwork/save', methods=['POST'])
@jwt_required
def save_SubNetwork(db: Graph):
    dataDict = json.loads(request.data)
    current_user = get_jwt_identity()
    SubNetwork.update_by_user(db, current_user, dataDict['id_activity'], dataDict['id_subnetwork'], dataDict['data'])
   
    return jsonify({"sucess": "Subnetwork saved."})

@account_controller.route("/network/logs",  methods=['GET'])
@jwt_required
def log_network(db: Graph):
    current_user = get_jwt_identity()
    id_network = request.args.get('network')

    networks_list = User.fetch_networks_available(db, current_user, id_network)

    if len(networks_list) <= 0:
        return jsonify({'json_list': []}), 200

    result = NetworkUserLog.query.filter_by(network_id=id_network).order_by(NetworkUserLog.created_on.desc())
    return jsonify(json_list=[i.serialize for i in result.all()])


@account_controller.route("/network/delete",  methods=['POST'])
@jwt_required
def delete_network(db: Graph):
    dataDict = json.loads(request.data)
    current_user = get_jwt_identity()
    Network.delete_by_user(db, current_user, dataDict["id"])
    return jsonify({"sucess": True, "message":"Rede removida."}), 202

@account_controller.route("/course/delete",  methods=['POST'])
@jwt_required
def delete_course(db: Graph):
    dataDict = json.loads(request.data)
    current_user = get_jwt_identity()
    Course.delete_by_user(db, current_user, dataDict["id"])
    return jsonify({"sucess": True, "message":"Rede removida."}), 202

@account_controller.route('/users/activity/subnetwork/get/id', methods=['GET'])
@jwt_required
def get_by_id_SubNetwork(db: Graph):
    current_user = get_jwt_identity()
    result = SubNetwork.fetch_by_id(db, current_user, request.args.get('id_activity'), request.args.get('id_subnetwork'))
    if result:
        result = SubNetwork.fetch_by_id(db, current_user, request.args.get("id_activity"), request.args.get("id_subnetwork"))
    else:
        sub = SubNetwork()
        sub.uuid = request.args.get('id_subnetwork')
        sub.all_data = "[]"
        db.push(sub)
        SubNetwork.create_relationship( db, current_user, request.args.get('id_activity'), request.args.get('id_subnetwork') )
        result = {'uuid': sub.uuid, 'all_data': "[]"}
        
    return jsonify(result)

@account_controller.route('/users/activity/save', methods=['POST'])
@jwt_required
def save_Network(db: Graph):
    dataDict = json.loads(request.data)
    current_user = get_jwt_identity()
    if 'data' in dataDict:
        result = Network.update_by_user(db, current_user, dataDict['id'], dataDict['data'], getCurrentDate())
    if 'name' in dataDict:
        result = Network.update_name_by_user(db, current_user, dataDict['id'], dataDict['name'], getCurrentDate())

    createLog(current_user, dataDict['id'], "Realizou alterações na rede.")
    return jsonify({"sucess": True, "message": "A Rede de atividades foi salva."})

@account_controller.route('/getTime', methods=['GET'])
def getCurrentTime():
    return jsonify({ "current_time": getCurrentDate() })

@account_controller.route('/users/activity/get/id', methods=['GET'])
@jwt_required
def get_by_id_Network(db: Graph):
    current_user = get_jwt_identity()
    result = Network.fetch_by_id(db, current_user, request.args.get("id"))

    return jsonify(result)

@account_controller.route('/users/course/get/id', methods=['GET'])
@jwt_required
def get_by_id_course(db: Graph):
    current_user = get_jwt_identity()
    course_id = request.args.get("id")
    result = db.run("MATCH (p:User{email:'%s'})-[r1]-(net:Network)-[r2]-(course:Course{id:%s}) return net" % (current_user, course_id)).data()[0]['net']
    return jsonify(result)

@account_controller.route('/users/activity/getAll', methods=['GET'])
@jwt_required
def getall_Network(db: Graph):
    current_user = get_jwt_identity()
    page = int(request.args.get("page"))-1
    size = int(request.args.get("page_size"))
    code = request.args.get("code")
    name = request.args.get("name")
    
    result = Network.fetch_all_by_user(db, current_user, size*page, size, code, name)

    return jsonify(result)

def generateUUID():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(18))

@account_controller.route('/users/activity/create', methods=['POST'])
@jwt_required
def create_Network(db: Graph):
    current_user = get_jwt_identity()
    dataDict = json.loads(request.data)
    
    atividade = make_network(db, current_user)
    
    return jsonify({"sucess": "activity created.", "name":atividade.id})

@account_controller.route('/users/activity/<string:network_id>/duplicate', methods=['POST'])
@jwt_required
def duplicate_Network(db: Graph, network_id):
    current_user = get_jwt_identity()
    #dataDict = json.loads(request.data)
    result = Network.fetch_by_id(db, current_user, network_id)
    
    atividade = make_network(db, current_user, course_name=f"{result['name']}_cópia", all_data=result['all_data'])    
    
    return jsonify({"sucess": "activity created.", "name":atividade.id})

def make_network(db, current_user, course_name='', url_moodle=None, token=None, course_id=None, all_data=[]):
    user = User.fetch_by_email(db, current_user )

    atividade = Network()
    atividade.id = generateUUID()
    #getQuantity
    qt = Network.getQuantity(db, current_user)
    num = str(qt) if qt != 0 else ""
    atividade.name = "Sem título "+num if len(course_name)==0 else course_name
    atividade.all_data = f"{all_data}"
    if url_moodle:
        atividade.token = token
        atividade.url = url_moodle
        atividade.course_id = course_id
    atividade.created_at = getCurrentDate()
    atividade.updated_at = getCurrentDate()
    atividade.attachment.add(user)
    db.push(atividade)
    
    return atividade

@account_controller.route('/users/register', methods=['POST'])
def register(db: Graph):
    dataDict = json.loads(request.data)
    if not dataDict['email'] or not dataDict['first_name'] or not dataDict['last_name'] or not dataDict['password']:
        return jsonify({"error": "`email`, `first_name`, `last_name` e `password` são obrigatórios."}), 400

    usuario = User.fetch_by_email(graph=db, email=dataDict['email'])#Usuario.query.filter_by(email=username,senha=getHash512(password)).first()
    if usuario:
        return jsonify({"error": "Email já cadastrado."}), 400

    usuario = User()
    usuario.email = dataDict['email']
    usuario.first_name = dataDict['first_name']
    usuario.last_name = dataDict['last_name']
    usuario.passwod = getHash512(dataDict['password'])
    db.push(usuario)
    user = UserObject(username=usuario.email, role='User', permissions=['foo', 'bar'])

    expires = datetime.timedelta(minutes=30)
    access_token = create_access_token(identity=user, expires_delta=expires)
    ret = {'token': access_token, 'username': usuario.email}

    return jsonify(ret), 200

@account_controller.route('/users/login', methods=['POST','GET'])
def login(db: Graph):
    
    try:
        dataDict = json.loads(request.data)
        usuario = User.fetch_by_email_and_password(db, email=dataDict['email'],password=getHash512(dataDict['password']))
        if not usuario:
            return jsonify({"error": "Email ou senha inválido."}), 400

        user = UserObject(username=usuario.email, role='Admin', permissions=['foo', 'bar'])

        expires = datetime.timedelta(minutes=120)
        access_token = create_access_token(identity=user, expires_delta=expires)
        ret = {'token': access_token, 'username': usuario.email}
        return jsonify(ret), 200

    except Exception as e:
        print( str(e) , file=sys.stderr)

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username