# coding: utf-8
from flask import Blueprint, render_template, Request

from .models import *

from py2neo import Graph

from flask_login import current_user, login_required,logout_user, login_user

start_controller = Blueprint('start_controller', __name__, template_folder='templates')

@start_controller.route('/')
def index(db: Graph):
    return "teste"