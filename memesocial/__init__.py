from flask import Flask, send_from_directory, request, make_response, abort
from os import path
from PIL import Image
from StringIO import StringIO
from flask_compress import Compress


app = Flask(__name__)
Compress(app)


def init(configObject):
    # this is not unheard of, pygame uses this trick though it's ugly.
    app.config.from_object(configObject)
    from models import db, all_tables
    global db, all_tables
    register_all_blueprints()


@app.route('/images/<filename>')
def get_image(filename):
    q = 'thumbnail' in request.args
    if q:
        try:
            img = Image.open(path.join(app.config['UPLOAD_FOLDER'], filename))
        except IOError:
            return abort(404)

        img.thumbnail(app.config.THUMBNAIL_SIZE)
        bufferd = StringIO()

        # return this in png?
        img.save(bufferd, 'PNG')
        contents = bufferd.getvalue()
        bufferd.close()
        response = make_response(contents)
        response.headers['Content-Type'] = 'image/jpeg'
        return response

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )


def register_all_blueprints():
    """
    Regsiter all of my blueprints
    """
    from api import api
    from frontend import frontend

    myBlueprints = [api, frontend]

    for blueprint in myBlueprints:
        app.register_blueprint(blueprint)
