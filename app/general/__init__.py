# coding=utf-8
from flask import Blueprint, render_template, redirect, session, url_for

account_controller = Blueprint('account_controller', __name__, template_folder='templates')

from . import controller