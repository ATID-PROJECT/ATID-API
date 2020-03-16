# coding=utf-8
from flask import Blueprint, render_template, redirect, session, url_for

portal_controller = Blueprint('portal_controller', __name__, template_folder='templates')

from . import network_controller
#from . import moodle