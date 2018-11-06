from htmlmin import minify
import os
import subprocess
from subprocess import Popen
from .models import *
import click

def default_config_app(app):
    @app.after_request
    def add_header(response):
        response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
        response.headers['Cache-Control'] = 'public, max-age=0'#2592000
        if response.content_type == u'text/html; charset=utf-8':
            response.direct_passthrough = False
            response.set_data(
                minify(response.get_data(as_text=True))
            )
            return response
        return response
    return app

    @app.cli.command()
    @click.argument('folder')
    def test(folder):
        d = dict(os.environ)
        d['FLASK_ENV'] = 'testing'
        d['ENV_FOR_DYNACONF'] = 'testing'
        # Disable sending emails during unit testing
        d['DISABLE_SEND_EMAIL'] = 'true'
        process = Popen('pipenv run flask create_db_tests; python -m unittest discover {0}'.format(folder),env=d, shell=True)
        process.communicate()

    @app.cli.command()
    def start():
        """Runs the set-up needed for local development."""
        Popen("x-terminal-emulator -e ./run-redis.sh", stdout=subprocess.PIPE, shell=True)
        Popen("x-terminal-emulator -e pipenv run celery worker -A app.celery --loglevel=info; /bin/bash", shell=True)
        Popen('pipenv run flask run', shell=True)