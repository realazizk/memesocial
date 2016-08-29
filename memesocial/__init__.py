from flask import Flask, send_from_directory, url_for
from os import environ
import tempfile

app = Flask(__name__)
app.config.from_object('memesocial.config')


from models import db, all_tables
from api import api


# XXX: FOR DEBUGGING
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
    myBlueprints = [api]

    for blueprint in myBlueprints:
        app.register_blueprint(blueprint)


doStuff()
