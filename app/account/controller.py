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

sys.path.append("..")
from app.JWTManager import jwt
import uuid 

import urllib.request, json 

source_moodle = "http://localhost:8090/"
url_moodle = "webservice/rest/server.php?wstoken={0}&wsfunction={1}&moodlewsrestformat=json"

@account_controller.route('/moodle/get', methods=['GET'])
@jwt_required
def getFunctionMoodle():
    function = request.args.get("function")
    #change default token to owener token
    token = "dabfde815d37f639e32db61f420ad46c"
    print(source_moodle+(url_moodle.format(token, function)))
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
def save_subActivity(db: Graph):
    dataDict = json.loads(request.data)
    current_user = get_jwt_identity()
    SubActivity.update_by_user(db, current_user, dataDict['id_activity'], dataDict['id_subnetwork'], dataDict['data'])
    print( dataDict['id_subnetwork'] )
    print( dataDict['data'] )
    return jsonify({"sucess": "Subnetwork saved."})

@account_controller.route('/users/activity/subnetwork/get/id', methods=['GET'])
@jwt_required
def get_by_id_subActivity(db: Graph):
    current_user = get_jwt_identity()
    result = SubActivity.fetch_by_id(db, current_user, request.args.get('id_activity'), request.args.get('id_subnetwork'))
    if result:
        result = SubActivity.fetch_by_id(db, current_user, request.args.get("id_activity"), request.args.get("id_subnetwork"))
    else:
        sub = SubActivity()
        sub.uuid = request.args.get('id_subnetwork')
        sub.all_data = "[]"
        db.push(sub)
        SubActivity.create_relationship( db, current_user, request.args.get('id_activity'), request.args.get('id_subnetwork') )
        result = {'uuid': sub.uuid, 'all_data': "[]"}
        print( "criado = " + sub.uuid)
    return jsonify(result)

@account_controller.route('/users/activity/save', methods=['POST'])
@jwt_required
def save_activity(db: Graph):
    dataDict = json.loads(request.data)
    current_user = get_jwt_identity()
    # (para fazer) restringir para editar apenas as atividades criadas pelo próprio usuário
    result = Activity.update_by_user(db, current_user, dataDict['id'], dataDict['data'])
    return jsonify({"sucess": "activity saved."})

@account_controller.route('/users/activity/get/id', methods=['GET'])
@jwt_required
def get_by_id_activity(db: Graph):
    current_user = get_jwt_identity()
    result = Activity.fetch_by_id(db, current_user, request.args.get("id"))
    return jsonify(result)


@account_controller.route('/users/activity/getAll', methods=['GET'])
@jwt_required
def getall_activity(db: Graph):
    current_user = get_jwt_identity()
    page = int(request.args.get("page"))-1
    size = int(request.args.get("page_size"))
    result = Activity.fetch_all_by_user(db, current_user, size*page, size)
    return jsonify(result)

@account_controller.route('/users/activity/create', methods=['POST'])
@jwt_required
def create_activity(db: Graph):
    current_user = get_jwt_identity()
    dataDict = json.loads(request.data)
    usuario = User.fetch_by_email(db, current_user )
    if not usuario:
        return jsonify({"error": "`email` são obrigatórios."}), 400

    atividade = Activity()
    atividade.id= ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(18))
    atividade.name = request.form.get("name")
    atividade.course_id = request.form.get("course_id")
    atividade.course_source = "localhost:8090"
    atividade.plataform = request.form.get("plataform")
    atividade.all_data = ""
    atividade.created_at = datetime.datetime.now().strftime('%F')
    atividade.updated_at = datetime.datetime.now().strftime('%F')
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

@account_controller.route('/users/authenticate', methods=['POST','GET'])
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