from flask import Flask, send_from_directory
from os import environ
from werkzeug.contrib.profiler import ProfilerMiddleware

app = Flask(__name__)
app.config.from_object('memesocial.config')
app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

from models import db, all_tables
from api import api
from frontend import frontend

# XXX: FOR DEBUGGING
if environ.get('TESTING') == '1':
    db.create_tables(all_tables)


@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )


def doStuff():
    register_all_blueprints()


def register_all_blueprints():
    """
    Regsiter all of my blueprints
    """
    myBlueprints = [api, frontend]

    for blueprint in myBlueprints:
        app.register_blueprint(blueprint)


doStuff()
