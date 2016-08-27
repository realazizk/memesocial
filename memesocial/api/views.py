from flask import Blueprint, request, abort, g, jsonify, url_for, session
from itsdangerous import Serializer
from ..models import User
from peewee import IntegrityError, fn, DoesNotExist
from functools import wraps
from memesocial import config

api = Blueprint(
    'api',
    __name__,
    url_prefix='/api'
)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return (jsonify({'errors': [{'detail': 'You are not allowed here sucker'}]}), 405)
        return f(*args, **kwargs)
    return decorated_function


@api.before_request
def before_request():
    g.s = Serializer(config.SECRET_KEY)
    print session.get('userData')
    g.user = session.get('userData', None)
    if g.user:
        g.user = g.s.loads(g.user)

# this will remove session from client and server side
@api.after_app_request
def remove_if_invalid(response):
    print session
    if "__invalidate__" in session:
        response.delete_cookie('session')
        session.pop('userData', None)

    return response


@api.route('/hello')
def hello():
    return 'Hello Mohamed'


@api.route('/register_user', methods=['POST'])
def reg():
    username = request.json.get('username')
    password = request.json.get('password')
    # if didn't pass username and password
    if username is None or password is None:
        abort(400)

    try:
        user = User.create(username=username, password=User.hash_password(
            password), active=True, online=True)
    except IntegrityError:
        return (jsonify({'errors': [{'detail': 'The username shall be unique'}]}), 422)
    return user.password


@api.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return (jsonify({'errors': [{'detail': 'Username and/or password is none'}]}), 422)
    try:
        user = User.get(User.username==username)
    except DoesNotExist:
        err = 'username'
    else:
        if user.verify_password(password):
            session['userData'] = g.s.dumps({
                'username': user.username,
                'id': user.id
            })
            return 'ALL GOOD BUDDY'
        else:
            err = 'password'
    print session
    return (jsonify(
        {
            'errors': [
                {
                    'detail': 'The %s is incorrect' % err
                }
            ]
        }
    ), 400)


@api.route('/logout')
@login_required
def logout():
    session["__invalidate__"] = True
    return (jsonify({'success': True}), 422)

@api.route('/whoami')
@login_required
def whoami():
    return g.user['username']
