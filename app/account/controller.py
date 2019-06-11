import sys
import hashlib
import json
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

#sys.path.append("..")
from app.JWTManager import jwt
import uuid 

import urllib.request, json 
import requests

source_moodle = "https://good-firefox-42.localtunnel.me"
url_moodle = "webservice/rest/server.php?wstoken={0}&wsfunction={1}&moodlewsrestformat=json"

def getCurrentDate():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def saveConnection( db, network_id, current_user, url, token ):
    query = f"MATCH (p:User{{email:'{current_user}'}})-[r1]-(net:Network{{id:'{network_id}'}}) \
            SET net.url = '{url}',\
                net.token = '{token}'\
                return net"
 
    db.run(query)

def registerCourse( db, current_id, network_id, current_user, fullname, shortname):
    
    course = Course()
    course.id = current_id
    course.fullname = fullname
    course.shortname = shortname
    course.network_id = network_id
    course.created_at = getCurrentDate()
    
    db.push(course)

    Network.addCourse(db, current_user, network_id, current_id)
    
def createChat(url_base, token, course_id, name, description):
    
    function = "local_wstemplate_handle_chat"
    params = f"&name={name}&description={description}&course_id={course_id}"
    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))
    r = requests.post( final_url, data={} )
    result = r.json()

    return "ok"

def createWiki(url_base, token, course_id, name, description, wikimode, firstpagetitle, defaultformat):
    
    function = "local_wstemplate_handle_wiki"
    params = f"&name={name}&description={description}&course_id={course_id}&wikimode={wikimode}&firstpagetitle={firstpagetitle}&defaultformat={defaultformat}"
    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))
    r = requests.post( final_url, data={} )
    result = r.json()

    return "ok"
    
def createGlossario(url_base, token, course_id, name, description, mainglossary, defaultapproval, editalways, allowduplicatedentries, allowcomments, usedynalink,
displayformat, approvaldisplayformat, entbypage, showalphabet, showall, showspecial, allowprintview):

    function = "local_wstemplate_handle_glossary"
    params = f"&name={name}&description={description}&course_id={course_id}&mainglossary={mainglossary}&defaultapproval={defaultapproval}&editalways={editalways}&\
        allowduplicatedentries={allowduplicatedentries}&allowcomments={allowcomments}&usedynalink={usedynalink}&displayformat={displayformat}&approvaldisplayformat={approvaldisplayformat}&\
        entbypage={entbypage}&showalphabet={showalphabet}&showall={showall}&showspecial={showspecial}&allowprintview={allowprintview}"
    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return "ok"

def createForum(url_base, token, course_id, name, description, type_forum, maxbytes, maxattachments, displaywordcount, forcesubscribe, trackingtype):
    
    function = "local_wstemplate_handle_forum"
    params = f"&name={name}&description={description}&course_id={course_id}&type={type_forum}&maxbytes={maxbytes}&\
        maxattachments={maxattachments}&displaywordcount={displaywordcount}&forcesubscribe={forcesubscribe}&trackingtype={trackingtype}"
    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))
    r = requests.post( final_url, data={} )
    result = r.json()

    return "ok"

def createExterntool(url_base, token, course_id, name, description, instructorchoicesendname, instructorchoicesendemailaddr, instructorchoiceacceptgrades,
 typeid,toolurl, securetoolurl, launchcontainer, resourcekey, password, instructorcustomparameters):
    function = "local_wstemplate_handle_lti"
    params = f"&name={name}&description={description}&course_id={course_id}&instructorchoicesendname={instructorchoicesendname}&instructorchoicesendemailaddr={int(instructorchoicesendemailaddr)}&\
        instructorchoiceacceptgrades={instructorchoiceacceptgrades}&typeid={typeid}&toolurl={toolurl}&securetoolurl={securetoolurl}&launchcontainer={getValueFromCheckbox(launchcontainer)}&resourcekey={resourcekey}&\
            password={password}&instructorcustomparameters={instructorcustomparameters}"
    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))
    
    r = requests.post( final_url, data={} )
    result = r.json()

    return "ok"

def getValueFromCheckbox(item):
    if len( str( item)) == 0:
        return 0
    else:
        return int(item)

def createDatabase(url_base, token, course_id, name, description, approval, manageapproved, comments, requiredentriestoview, maxentries,
timeavailablefrom,timeavailableto, timeviewfrom, timeviewto):
    
    function = "local_wstemplate_handle_data"
    params = f"&name={name}&description={description}&course_id={course_id}&approval={getValueFromCheckbox(approval)}&manageapproved={getValueFromCheckbox(manageapproved)}&comments={getValueFromCheckbox(comments)}&\
    requiredentriestoview={getValueFromCheckbox(requiredentriestoview)}&maxentries={getValueFromCheckbox(maxentries)}&timeavailablefrom={timeavailablefrom}&timeavailableto={timeavailableto}&\
    timeviewfrom={timeviewfrom}&timeviewto={timeviewto}"
    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))
    r = requests.post( final_url, data={} )
    result = r.json()

    return "ok"

def createChoiceOption(url_base, token, choiceid, text, maxanswers):
    

    function = "local_wstemplate_handle_choice_option"
    params = f"&choiceid={int(choiceid)}&text={text}&maxanswers={int(maxanswers)}"
    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))
    
    r = requests.post( final_url, data={} )
    result = r.json()

    return "ok"

def createQuiz(url_base, token, course_id, name, description, timeopen, timeclose):

    print("____________", file=sys.stderr)
    function = "local_wstemplate_handle_quiz"
    params = f"&course_id={course_id}&name={name}&description={description}&timeopen={timeopen}&timeclose={timeclose}"
    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))
    
    print(final_url, file=sys.stderr)
    r = requests.post( final_url, data={} )
    result = r.json()

    return "ok"

def createChoice(url_base, token, course_id, name, description, allowupdate, allowmultiple, limitanswers, choice_questions):
    
    function = "local_wstemplate_handle_choice"

    params = f"&name={name}&description={description}&course_id={course_id}&allowupdate={getValueFromCheckbox(allowupdate)}&allowmultiple={getValueFromCheckbox(allowmultiple)}&limitanswers={getValueFromCheckbox(limitanswers)}"
    final_url = str( url_base + "/" +(url_moodle.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    for c in choice_questions:
        createChoiceOption(url_base, token, result['id'], c, 0)
        
    return "ok"

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

def createQuestion(item, url_base, token, course_id):
    
    label = str(item['label']).lower()
    
    if label == "chat":
        return createChat( url_base, token, course_id, item['name'], item['description'] )
    elif label == "database":
        return createDatabase( url_base, token, course_id, item['name'], item['description'], item['approval_required'], item['allow_edit_approval_entries'], item['allow_comment'], 
        item['required_before_viewing'], item['max_entries'], item['open_date'], item['end_date'], item['read_only'], item['read_only_end'])
    elif label == "forum":
        return createForum( url_base, token, course_id, item['name'], item['description'], item['type_forum'], item['maxbytes'], item['maxattachments'], item['displaywordcount'], item['forcesubscribe'], item['trackingtype'] )
    elif label == "externtool":
        return createExterntool( url_base, token, course_id, item['name'], item['description'], item['show_description_course'], item['show_activity'], item['show_description_activity'],
        item['pre_config_url'], item['url_tool'], item['url_tool_ssl'], item['pre_config'], item['key_consumer'], item['key_secret'], item['custom_params'] )
    elif label == "glossario":
        return createGlossario( url_base, token, course_id, item['name'], item['description'], item['type_glossario'], item['allow_new_item'], item['allow_edit'],
        item['allow_repeat_item'],item['allow_comments'],item['allow_automatic_links'],item['type_view'],item['type_view_approved'],item['num_items_by_page'],
        item['show_alphabet'],item['show_todos'],item['show_special'],item['allow_print'] )
    elif label == "wiki":
        return createWiki( url_base, token, course_id, item['name'], item['description'], item['wikimode'], item['firstpagetitle'], item['defaultformat'])
    elif label == "choice":
        return createChoice( url_base, token, course_id, item['name'], item['description'], item['allow_choice_update'],item['allow_multiple_choices'],
        item['allow_limit_answers'], item['choice_questions'])
    elif label == "quiz":
        return createQuiz( url_base, token, course_id, item['name'], item['description'], item['open_date'], item['end_date'])
    elif label == "assign":
        return createAssign(token, course_id, item['name'], item['description'], item['wikimode'], item['firstpagetitle'], item['defaultformat'])

@account_controller.route('/moodle/new_course', methods=['POST'])
@jwt_required
def makeCourse(db: Graph):
    current_user = get_jwt_identity()
    dataDict = request.get_json(force=True)

    network_id = dataDict["network_id"]
    fullname = dataDict["fullname"]
    shortname = dataDict["shortname"]
    
    network = db.run("MATCH (p:User{email:'%s'})-[r1]-(net:Network{id:'%s'}) return net" % (current_user, network_id)).data()[0]['net']
    all_questions = db.run("MATCH (p:User{email:'%s'})-[r1]-(net:Network{id:'%s'})-[r2:HAS_QUESTIONS]-(q) return q" % (current_user, network_id)).data()

    result = createCourse(network['url'], network['token'], fullname, shortname, db, network_id, current_user)
    id_course = result['id']

    for question in all_questions:
        item = dict(question['q'])
        createQuestion( item, network['url'] , network['token'], int(id_course))
    
    return jsonify({"message": "curso criado com sucesso", "status": 200}), 200
    

@account_controller.route('/moodle/test', methods=['GET'])
@jwt_required
def moodleTest(db: Graph):
    function = "core_webservice_get_site_info"
    current_user = get_jwt_identity()

    url_base = request.args.get("url")
    network_id = request.args.get("network_id")
    token = request.args.get("token")

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

@account_controller.route('/users/activity/subnetwork/save', methods=['POST'])
@jwt_required
def save_SubNetwork(db: Graph):
    dataDict = json.loads(request.data)
    current_user = get_jwt_identity()
    SubNetwork.update_by_user(db, current_user, dataDict['id_activity'], dataDict['id_subnetwork'], dataDict['data'])
   
    return jsonify({"sucess": "Subnetwork saved."})

@account_controller.route("/network/delete",  methods=['POST'])
@jwt_required
def delete_network(db: Graph):
    dataDict = json.loads(request.data)
    current_user = get_jwt_identity()
    Network.delete_by_user(db, current_user, dataDict["id"])
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

    return jsonify({"sucess": True, "message": "A Rede de atividades foi salva."})

@account_controller.route('/getTime', methods=['GET'])
def getCurrentTime():
    return jsonify({ "current_time": getCurrentDate() })

@account_controller.route('/users/activity/get/id', methods=['GET'])
@jwt_required
def get_by_id_Network(db: Graph):
    current_user = get_jwt_identity()
    result = Network.fetch_by_id(db, current_user, request.args.get("id"))
    print( result, file=sys.stderr)
    return jsonify(result)

@account_controller.route('/users/activity/getAll', methods=['GET'])
@jwt_required
def getall_Network(db: Graph):
    current_user = get_jwt_identity()
    page = int(request.args.get("page"))-1
    size = int(request.args.get("page_size"))
    result = Network.fetch_all_by_user(db, current_user, size*page, size)

    return jsonify(result)

def generateUUID():
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(18))

@account_controller.route('/users/activity/create', methods=['POST'])
@jwt_required
def create_Network(db: Graph):
    current_user = get_jwt_identity()
    dataDict = json.loads(request.data)
    usuario = User.fetch_by_email(db, current_user )
    if not usuario:
        return jsonify({"error": "`email` são obrigatórios."}), 400

    atividade = Network()
    atividade.id = generateUUID()
    #getQuantity
    qt = Network.getQuantity(db, current_user)
    num = str(qt) if qt != 0 else ""
    atividade.name = "Sem título "+num
    atividade.all_data = "[]"
    atividade.created_at = getCurrentDate()
    atividade.updated_at = getCurrentDate()
    atividade.attachment.add(usuario)
    db.push(atividade)
    return jsonify({"sucess": "activity created.", "name":atividade.id})


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
    ret = {'token': access_token}

    return jsonify(ret), 200

@account_controller.route('/users/login', methods=['POST','GET'])
def login(db: Graph):
    dataDict = json.loads(request.data)
    
    usuario = User.fetch_by_email_and_password(db, email=dataDict['email'],password=getHash512(dataDict['password']))#Usuario.query.filter_by(email=username,senha=getHash512(password)).first()
    if not usuario:
        return jsonify({"error": "Email ou senha inválido."}), 400

    user = UserObject(username=usuario.email, role='Admin', permissions=['foo', 'bar'])

    expires = datetime.timedelta(minutes=120)
    access_token = create_access_token(identity=user, expires_delta=expires)
    ret = {'token': access_token, 'username': usuario.email}
    return jsonify(ret), 200

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username