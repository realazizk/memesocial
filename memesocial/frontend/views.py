from flask import Blueprint, render_template, send_from_directory, abort, session, g,\
    jsonify
from functools import wraps
import os
from itsdangerous import Serializer
from memesocial import config
from memesocial.api import views as apiViews
from json import loads


frontend = Blueprint(
    'frontend',
    __name__,
    template_folder='templates'
)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return (jsonify({'errors': [{'detail': 'You are not allowed here sucker'}]}), 405)
        return f(*args, **kwargs)
    return decorated_function


@frontend.before_request
def before_request():
    g.s = Serializer(config.SECRET_KEY)
    g.user = session.get('userData', None)
    if g.user:
        g.user = g.s.loads(g.user)


@frontend.route('/static/<dire>/<filename>')
def serve_static(dire, filename):
    """
    this endpoint serves the static files in static
    """
    if dire not in set(['js', 'fonts', 'css', 'imgs']):
        abort(404)
    root_dir = os.path.dirname(os.path.realpath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static', dire), filename)


@frontend.route('/dashboard')
def dashboard():
    return str(g.user['id'])


@frontend.route('/profile/<int:userid>')
def user_profile(userid):
    currUser = loads(apiViews.user_info(userid)[0].data)
    return render_template('profile.jhtml', userid=userid, userData=currUser, isLogged=g.user is not None)


@frontend.route('/')
def index():
    return render_template('index.jhtml')
