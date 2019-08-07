# coding: utf-8
from flask import Blueprint, render_template, Request
from .models import *
from py2neo import Graph
from flask_login import current_user, login_required,logout_user, login_user

start_controller = Blueprint('start_controller', __name__, template_folder='templates')

from .questions import *

from urllib.parse import urlparse
import sys
@start_controller.route('/')
def index(db: Graph):
    o = request.remote_addr
    host = o
    print(host+"...", file=sys.stderr)
    return "API ATID"