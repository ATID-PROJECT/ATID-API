# coding: utf-8
from .questions import *
from dynaconf import settings
from flask import Blueprint, render_template, request, jsonify
from .models import *
from py2neo import Graph
from flask_login import current_user, login_required, logout_user, login_user
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

from app.sqlite_models import *
from app.database import sqlite_db
import sys
import requests

start_controller = Blueprint(
    'start_controller',
    __name__,
    template_folder='templates')


def createLog(current_user, network_id, description):

    try:
        log = NetworkUserLog(
            user_id=current_user,
            network_id=network_id,
            description=description)
        sqlite_db.session.add(log)
        sqlite_db.session.commit()
    except Exception as e:
        print('*************------------------++++++++++++', file=sys.stderr)
        print(str(e), file=sys.stderr)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno, file=sys.stderr)


def get_enrolled(db, current_user, network_id, course_id):
    network = db.run(
        "MATCH (p:User{email:'%s'})-[r1]-(net:Network{id:'%s'}) return net" %
        (current_user, network_id)).data()[0]['net']

    url_base = network['url']
    token = network['token']

    function = "core_enrol_get_enrolled_users"
    params = f"&courseid={course_id}"
    final_url = str(url_base + "/" +
                    (settings.URL_MOODLE.format(token, function + params)))

    r = requests.post(final_url, data={})
    result = r.json()

    return result


@start_controller.route('/')
def index(db: Graph):
    o = request.remote_addr
    host = o
    print(host + "...", file=sys.stderr)
    return "API ATID"


@start_controller.route('/get_enrolled_users', methods=['GET', 'POST'])
@jwt_required
def get_enrolled_users(db: Graph):
    current_user = get_jwt_identity()

    network_id = request.args.get('network_id')
    course_id = request.args.get('course_id')

    result = get_enrolled(db, current_user, network_id, course_id)

    return jsonify(result)
