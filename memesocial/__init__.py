from flask import Flask

app = Flask(__name__)
app.config.from_object('memesocial.config')


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
