import sys
import hashlib
import json
from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import (
    create_access_token,
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

@account_controller.route('/users/activity', methods=['POST'])
def create_activity(db: Graph):
    dataDict = json.loads(request.data)
    usuario = User.fetch_by_email(db, dataDict['email'] )
    if not usuario:
        return jsonify({"error": "`email` são obrigatórios."}), 400

    atividade = Activity()
    atividade.name = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(12))
    atividade.all_data = ""
    atividade.attachment.add(usuario)

    db.push(atividade)

    return jsonify({"sucess": "activity created.", "name":atividade.name})


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

    expires = datetime.timedelta(minutes=1)
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

    expires = datetime.timedelta(minutes=1)
    access_token = create_access_token(identity=user, expires_delta=expires)
    ret = {'token': access_token, 'username': usuario.email}
    return jsonify(ret), 200

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username