# coding: utf-8
from flask import Blueprint, render_template, Request

from .models import *

from ext.database import SQLAlchemy

from flask_login import current_user, login_required,logout_user, login_user

start_controller = Blueprint('start_controller', __name__, template_folder='templates')

@start_controller.route('/')
def index(db: SQLAlchemy):
    return "teste"