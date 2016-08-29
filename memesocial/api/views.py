from flask import Blueprint, request, abort, g, jsonify, session
from itsdangerous import Serializer
from ..models import User, FollowerRelation, Image, Heart
from peewee import IntegrityError, DoesNotExist
from functools import wraps
from memesocial import config, utils
import datetime

__author__ = "Mohamed Aziz Knani"

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
    g.user = session.get('userData', None)
    if g.user:
        g.user = g.s.loads(g.user)


# this will remove session from client and server side
@api.after_app_request
def remove_if_invalid(response):
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
        User.create(username=username, password=User.hash_password(
            password), active=True, online=True)
        # do something with user?
    except IntegrityError:
        return (jsonify({'errors': [{'detail': 'The username shall be unique'}]}), 422)
    return (jsonify({
        'success': 'Created user succefully'
    }), 200)


@api.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return (jsonify({'errors': [{'detail': 'Username and/or password is none'}]}), 422)
    try:
        user = User.get(User.username == username)
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


@api.route('/update_profile_image', methods=['POST'])
@login_required
def update_profile_image():
    imageFile = request.get_data()
    if imageFile is not None:
        filename = utils.save_file(
            imageFile
        )
        query = User.update(imageProfile=config.SITE_URL + '/images/' + filename)\
                    .where(User.id == g.user['id'])
        if not query.execute():
            return (jsonify({'errors': [{'detail': 'Could not upload image'}]}), 422)
        return (jsonify({'success': [{'detail': 'Uploaded image succefully'}]}), 200)


@api.route('/update_cover_image', methods=['POST'])
@login_required
def update_cover_image():
    imageFile = request.get_data()
    if imageFile is not None:
        filename = utils.save_file(
            imageFile
        )
        query = User.update(coverProfile=config.SITE_URL + '/images/' + filename)\
                    .where(User.id == g.user['id'])
        if not query.execute():
            return (jsonify({'errors': [{'detail': 'Could not upload image'}]}), 422)
        return (jsonify({'success': [{'detail': 'Uploaded image succefully'}]}), 200)


@api.route('/follow/<int:leaderid>')
@login_required
def followLeader(leaderid):
    if leaderid == g.user['id']:
        return (
            jsonify(
                {'errors': [{'detail': 'You can not follow yourself silly'}]}), 405
        )
    # if there is an integrity error (the relation is already existant)
    try:
        FollowerRelation.create(
            follower=g.user['id'],
            leader=leaderid
        )
    except IntegrityError:
        return (
            jsonify(
                {'errors': [{'detail': 'You are already following this user'}]}), 405
        )

    return (jsonify({'success': 'Followed user succefully'}))


@api.route('/unfollow/<int:leaderid>')
@login_required
def unfollowLeader(leaderid):
    r = FollowerRelation.delete().where(FollowerRelation.follower == g.user['id'], FollowerRelation.leader == leaderid)
    if not bool(r.execute()):
        return (jsonify({'error': 'It seems that no relation like exist'}), 202)
    return (jsonify({'success': 'Unfollowed user succefully'}), 200)


@api.route('/create_content', methods=['POST'])
@login_required
def createcontent():
    imageFile = request.json.get('image')
    description = request.json.get('desc')
    if not (imageFile is None or description is None):
        filename = utils.save_file(
            utils.decode_image(imageFile)
        )
        query = Image.insert(url=config.SITE_URL + '/images/' + filename,
                             owner=g.user['id'], description=description,
                             date=datetime.datetime.now())
        if not bool(query.execute()):
            return (jsonify({'errors': [{'detail': 'Could not upload image'}]}), 422)
        return (jsonify({'success': [{'detail': 'Uploaded image succefully'}]}), 200)


# any logged user shall get the followers and leaders list
@api.route('/relations/<int:userid>')
@login_required
def rels(userid):
    # the users that are following him
    followers = FollowerRelation.select(FollowerRelation.follower).where(
        FollowerRelation.leader == userid).iterator()
    # the users that he follows
    leaders = FollowerRelation.select(FollowerRelation.leader).where(
        FollowerRelation.follower == userid).iterator()
    followerList = []
    leadersList = []
    for f in followers:
        followerList.append(
            {
                'id': f.follower.id,
                'username': f.follower.username,
                'profile_image': f.follower.imageProfile
            }
        )
    for l in leaders:
        leadersList.append(
            {
                'id': l.leader.id,
                'username': l.leader.username,
                'profile_image': l.leader.imageProfile
            }
        )
    return (
        jsonify({
            'followers': followerList,
            'leaders': leadersList
        }), 200
    )


@api.route('/user/<int:userid>')
def user_info(userid):
    someKindOfUser = User.get(User.id == userid)
    data = {}
    data['username'] = someKindOfUser.username
    data['profile_image'] = someKindOfUser.imageProfile
    data['cover_image'] = someKindOfUser.coverProfile
    data['id'] = someKindOfUser.id

    return (
        jsonify(data),
        200
    )


# anyone could get user data like users: photos username...
@api.route('/user_posts/<int:userid>')
def user_posts(userid):
    # where to start user images?
    # second parmter is default value, REFACTOR
    start = int(request.args.get('start', '1'))
    limit = int(request.args.get('limit', '10'))

    # so this gonna return user data + next page (if it exists)
    # TODO: get number of hearts and check if user is logged in if yes check if he already liked it, also get number of comments
    bruttoData = Image.select().where(Image.owner == userid).order_by(Image.id).offset(start - 1).limit(limit)
    userContent = []
    for b in bruttoData:
        userContent.append({
            'id': b.id,
            'url': b.url,
            'description': b.description,
            'date': b.date
        })
    # i don't need previous for now I'm gonna do a infite scroll
    nextData = Image.select().where(Image.owner == userid).order_by(Image.id).offset(start + limit - 1).limit(limit).count()
    retData = {
        'data': userContent
    }
    if nextData != 0:
        retData['next'] = utils.form_url(
            (config.SITE_URL, request.path), {
                'start': start + limit,
                'limit': limit
            }
        )
    if not retData['data']:
        return (jsonify({'errors': [{'detail': 'No more Posts'}]}), 422)
    return (jsonify(retData), 200)


@api.route('/heartit/<int:contentid>')
@login_required
def heart_it(contentid):
    # my endpoint to heart this content with contentid
    try:
        # I don't need the returned heart instance
        Heart.create(imageId=contentid, userId=g.user['id'])
    except IntegrityError:
        return (jsonify({'error': 'You sneaky bastard you already hearted this content.'}), 202)
    return (jsonify({'success': 'Nice you hearted this content.'}), 200)


@api.route('/unheartit/<int:contentid>')
@login_required
def unheart_it(contentid):
    # my endpoint to unheart this content with contentid

    e = Heart.delete().where(Heart.imageId == contentid, Heart.userId == g.user['id'])
    if not bool(e.execute()):
        return (jsonify({'error': 'You sneaky bastard you did not even heart this content'}), 202)
    return (jsonify({'success': 'Nice you unhearted this content.'}), 200)



@api.route('/news_feed')
@login_required
def get_news_feed():
    # get news feed, come up with some kind of algorithm/formula that depends on time, and users relation (how many hearts he gave his leader)
    # and how many comments they share.
    pass


@api.route('/maybe_like')
@login_required
def suggest_leaders():
    # so this will suggest some leaders, this will be a complexe algorithm with lots of number crunching
    # So my idea is to build a network with a number n of layers (layers of user network)?
    # I will call this algorithm Frank (FollowersRank)
    # I will take a look at twitters tunkrank http://thenoisychannel.com/2009/01/13/a-twitter-analog-to-pagerank
    pass
