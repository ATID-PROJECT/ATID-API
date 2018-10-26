import sys
import hashlib
from flask import Flask, jsonify, request, make_response
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)
from .UserObject import UserObject
from ext.database import SQLAlchemy
import datetime
from . import account_controller

from app.models import *

sys.path.append("..")
from app.JWTManager import jwt

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

@account_controller.route('/users/authenticate', methods=['POST','GET'])
def login(db: SQLAlchemy):
    request_json = request.get_json()
    try:
        username = request_json.get('username')
        password = request_json.get('password')
    except AttributeError as e:
        return jsonify({"error": "'username' e 'password' são obrigatórios."}), 400
    
    # Buscar 
    usuario = Usuario.query.filter_by(email=username,senha=getHash512(password)).first()
    if not usuario:
        return jsonify({"error": "Usuário ou senha inválido."}), 400

@jwt.user_identity_loader
def user_identity_lookup(user):
    return user.username