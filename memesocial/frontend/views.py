from flask import Blueprint, render_template, send_from_directory, abort, session, g,\
    jsonify, request
from functools import wraps
import os
from itsdangerous import Serializer
from memesocial import app
from memesocial.api import views as apiViews
from json import loads

frontend = Blueprint('frontend', __name__, template_folder='templates')


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if g.user is None:
            return (jsonify(
                {'errors': [{'detail': 'You are not allowed here sucker'}]}),
                405)
        return f(*args, **kwargs)

    return decorated_function


@frontend.before_request
def before_request():
    g.s = Serializer(app.config['SECRET_KEY'])
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
    return send_from_directory(
        os.path.join(root_dir, 'static', dire), filename)


@frontend.route('/dashboard')
@login_required
def dashboard():
    maybeLike = loads(apiViews.suggest_leaders()[0].data)
    usrData = loads(apiViews.user_info(g.user['id'])[0].data)
    return render_template(
        'dashboard.jhtml', isLogged=True, maybeLike=maybeLike, currUser=usrData, userData=None)


@frontend.route('/profile/<int:userid>')
def user_profile(userid):
    currUser = loads(apiViews.user_info(userid)[0].data)
    relations = loads(apiViews.rels(userid)[0].data)
    if 'error' in currUser:
        abort(404)
    try:
        il = g.user is not None
        usrData = loads(apiViews.user_info(g.user['id'])[0].data)
    except:
        il = False
        usrData = None

    myPage = True if il and g.user.get('id') == userid else False

    if il:
        usrData = loads(apiViews.user_info(g.user['id'])[0].data)

    if myPage:
        isFollowing = False
    elif il:
        isFollowing = False
        for follower in relations['followers']:
            if follower['id'] == g.user['id']:
                isFollowing = True
                break
    else:
        isFollowing = False

    return render_template(
        'profile.jhtml',
        currUser=usrData,
        userid=userid,
        userData=currUser,
        isLogged=il,
        myPage=myPage,
        relations=relations,
        isFollowing=isFollowing)


@frontend.route('/')
def index():
    return render_template('index.jhtml')


@frontend.route('/content/<int:imageid>')
def serve_image(imageid):
    try:
        il = g.user is not None
        usrData = loads(apiViews.user_info(g.user['id'])[0].data)
    except:
        il = False
        usrData = None
    content, status = apiViews.gcontent(imageid)
    if status != 200:
        abort(400)

    if 'modal' in request.args:
        renderName = 'image_modal.jhtml'
    else:
        renderName = 'images.jhtml'

    myContent = loads(content.data)['success']
    # TODO: fix this hacky shit ( I need to pass all my variables since
    # images.jhtml inherits from content.jhtml)
    return render_template(
        renderName,
        isLogged=il,
        isMyContent=il and myContent['owner']['id'] == g.user['id'],
        userData=None, relations=None, myContent=myContent, isHearted=il and
        filter(lambda x: x['id'] == g.user['id'], myContent['hearters']) != [],
        isFollowing=il and filter(lambda x: x['id'] == g.user['id'], loads(
            apiViews.rels(myContent['owner']['id'])[0].data)['followers']),
        currUser=usrData
    )
