from flask import Flask, send_from_directory, url_for
from models import db, all_tables


app = Flask(__name__)
app.config.from_object('memesocial.config')


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
    from api import api

    myBlueprints = [api]

    for blueprint in myBlueprints:
        app.register_blueprint(blueprint)


doStuff()
