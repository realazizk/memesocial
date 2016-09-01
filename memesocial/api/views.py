from __future__ import division
from flask import Blueprint, request, g, jsonify, session
from itsdangerous import Serializer
from ..models import User, FollowerRelation, Image, Heart, Comment
from peewee import IntegrityError, DoesNotExist
from functools import wraps
from memesocial import config, utils
import datetime
from retcodes import USERNAME_NOT_FOUND, PASSWORD_NOT_FOUND, EMAIL_NOT_FOUND, WRONG_EMAIL,\
    SHORT_USERNAME, ALREADY_REGISTERED_USERNAME, USERNAME_AVAIL, EMAIL_NON_VALID, ALREADY_REGISTERED_EMAIL,\
    EMAIL_AVAIL


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
        session.pop('__invalidate__', None)
    return response


@api.route('/hello')
def hello():
    return 'Hello Mohamed'


@api.route('/register_user', methods=['POST'])
def reg():
    from validate_email import validate_email

    username = request.json.get('username')
    password = request.json.get('password')
    email = request.json.get('email')

    if not username:
        return (jsonify({'error': {'detail': 'Specify a username', 'code': USERNAME_NOT_FOUND}}), 400)
    if not password:
        return (jsonify({'error': {'detail': 'Specify a password', 'code': PASSWORD_NOT_FOUND}}), 400)
    if not email:
        return (jsonify({'error': {'detail': 'Specify an email', 'code': EMAIL_NOT_FOUND}}), 400)

    try:
        # I don't trust the users though javascript the frontend part will take care of this
        if not validate_email(email):
            return (jsonify({'error': {'detail': 'Wrong email', 'code': WRONG_EMAIL}}), 400)

        if valid_username(username)[1] == 400:
            return valid_username(username)

        User.create(username=username, password=User.hash_password(
            password), active=True, online=True, email=email)
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
            return (jsonify({'success': 'Logged in succefully'}), 200)
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
    return (jsonify({'success': True}), 200)


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


@api.route('/content/<int:cid>')
def gcontent(cid):
    # every one can see the content
    try:
        i = Image.get(Image.id == cid)
    except DoesNotExist:
        return (jsonify({'errors': [{'detail': 'Content does not exist'}]}), 422)
    hearters = Heart.select().where(Heart.imageId == i.id)
    commentors = Comment.select().where(Comment.imageId == i.id)
    hs = []
    cm = []
    for hearter in hearters:
        hs.append({
            'username': hearter.userId.username,
            'image_profile': hearter.userId.imageProfile,
            'id': hearter.userId.id
        })
    for comm in commentors:
        cm.append({
            'username': comm.usrId.username,
            'image_profile': comm.usrId.imageProfile,
            'id': comm.usrId.id
        })
    return (jsonify({'success': [{'detail': 'Request made succefully', 'hearters': hs, 'commentors': cm}]}), 200)


@api.route('/create_content', methods=['POST'])
@login_required
def createcontent():
    imageFile = request.json.get('image')
    description = request.json.get('desc')
    if not (imageFile is None or description is None):
        filename = utils.save_file(
            utils.decode_image(imageFile)
        )
        img = Image(url=config.SITE_URL + '/images/' + filename,
                    owner=g.user['id'], description=description,
                    date=datetime.datetime.now())
        if not bool(img.save()):
            return (jsonify({'errors': [{'detail': 'Could not upload image'}]}), 422)
        return (jsonify({'success': [{'detail': 'Uploaded image succefully',
                                      'contentid': img.id}]}), 200)


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


@api.route('/comment', methods=['POST'])
@login_required
def comment_on_something():
    contentid = request.json.get('content_id')
    comment_content = request.json.get('comment_content')

    if contentid and comment_content:
        # if image exists, foreign key exception don't seem to work
        query = Image.select().where(Image.id == contentid)
        if query.exists():
            Comment.insert(
                body=comment_content,
                date=datetime.datetime.now(),
                usrId=g.user['id'],
                imageId=contentid
            ).execute()
        else:
            return (jsonify({'error': 'Content does not exist'}), 404)
        return (jsonify({'success': 'Inserted comment succefully'}))
    else:
        return (jsonify({'errors': ['Please pass a contentid and comment content']}), 400)


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
    import json
    # my algorithm is based on the idea of facebook's edgerank described in edgerank.net
    # I called this ContentRank or Crank for short

    # I need to play with the numbers to see if this gives realistic scores?

    # Crank(x, y) = (1/(tx+1)) * Affinity(Owner(x), y)
    # Affinity(x, y) = (|| followers(x) intersection followers(y) || / 100) + (|| leaders(x) intersection leaders(y) || / 100) + (hearts(x, y)/10) + (hearts(y, x)/30)

    start = int(request.args.get('start', '1'))
    limit = int(request.args.get('limit', '10'))

    # get posts of leaders from last couple of hours
    leaders = FollowerRelation.select(FollowerRelation.leader).where(FollowerRelation.follower == g.user['id'])
    posts = Image.select().where(Image.owner << leaders).offset(start - 1).limit(limit)
    psts = []

    result = json.loads(rels(g.user['id'])[0].data)
    iFollowers = set(map(lambda x: x['id'], result['followers']))
    iLeader = set(map(lambda x: x['id'], result['leaders']))

    def hearts(x, y):
        usrImgs = Image.select(Image.id).where(Image.owner == y)
        return Heart.select().where(Heart.imageId << usrImgs).count()

    for post in posts:
        diff = datetime.datetime.now() - post.date
        minutesElapsed = divmod(diff.days * 86400 + diff.seconds, 60)

        result = json.loads(rels(post.owner.id)[0].data)
        lFollower = set(map(lambda x: x['id'], result['followers']))
        lLeader = set(map(lambda x: x['id'], result['leaders']))

        psts.append({
            'url': post.url,
            'id': post.id,
            'description': post.description,
            'ouser': post.owner.username,
            'oimg': post.owner.imageProfile,
            'score': 0.1 + (1 / (minutesElapsed[0] + 1)) * (((len(iFollowers.intersection(lFollower)) / 100) + (len(iLeader.intersection(lLeader)) / 100)) + (hearts(g.user['id'], post.owner.id) / 10) + (hearts(post.owner.id, g.user['id']) / 30))
        })

    # nextData = Image.select().where(Image.owner << leaders).offset(start + limit - 1).limit(limit).count()
    return (jsonify(psts), 200)


@api.route('/valid_username/<username>')
def valid_username(username):
    # return if a username is not already taken.
    if len(username) <= 4:
        return (jsonify({'error': {'detail': 'the username should be more than 4 caracters long',
                                   'code': SHORT_USERNAME}}), 400)
    query = User.select().where(User.username == username)
    if query.exists():
        return (jsonify({'error': {'detail': 'The username is already registerd', 'code': ALREADY_REGISTERED_USERNAME}}), 400)
    else:
        return (jsonify({'success': {'detail': 'The username is available', 'code': USERNAME_AVAIL}}), 200)


@api.route('/valid_email/<email>')
def valid_email(email):
    # return if a email is not already taken.
    from validate_email import validate_email

    if not validate_email(email):
        return (jsonify({'error': {'detail': 'The email is not valid',
                                   'code': EMAIL_NON_VALID}}), 400)
    query = User.select().where(User.email == email)
    if query.exists():
        return (jsonify({'error': {'detail': 'The email is associated to another user', 'code': ALREADY_REGISTERED_EMAIL}}), 400)
    else:
        return (jsonify({'success': {'detail': 'The email is available', 'code': EMAIL_AVAIL}}), 200)


@api.route('/maybe_like')
@login_required
def suggest_leaders():
    import json
    # My dumb algorithm, for liklyhood calculations, this is very dumb and straitforward but it may work
    # + This is processer heavy calculations that needs to be done in each request duh.

    # MY formula for now is (the paper is in my drawer):
    # L(x, y) = f(x, y) + CLS(x, y) + CFS(x, y) * 1 / 2.04

    # get current followers/leaders list.
    result = json.loads(rels(g.user['id'])[0].data)
    followers = set(map(lambda x: x['id'], result['followers']))
    # I only need leaders coz the user is interested by them lol
    myNetwork = set(map(lambda x: x['id'], result['leaders']))

    d = {}

    for eachNode in myNetwork:
        ldrs = set(map(lambda x: x['id'], json.loads(rels(eachNode)[0].data)['leaders']))
        for eachLeader in ldrs:
            if eachLeader in myNetwork or eachLeader == g.user['id']:
                continue
            x = 1
            if eachLeader in followers:
                x = 0.04

            res = json.loads(rels(eachLeader)[0].data)
            followers1 = set(map(lambda x: x['id'], res['followers']))
            leaders1 = set(map(lambda x: x['id'], res['leaders']))

            d[eachLeader] = (x + (len(followers1.intersection(myNetwork)) / len(followers1.union(followers))) + (len(leaders1.intersection(followers)) / len(leaders1.union(myNetwork)))) / 2.04

    for eachNode in followers.difference(myNetwork):
        if eachNode in d:
            continue
        # I'm in followers list duh
        res = json.loads(rels(eachNode)[0].data)
        followers1 = set(map(lambda x: x['id'], res['followers']))
        leaders1 = set(map(lambda x: x['id'], res['leaders']))

        d[eachNode] = (0.04 + (len(followers1.intersection(followers)) / len(followers1.union(followers))) + (len(leaders1.intersection(myNetwork)) / len(leaders1.union(myNetwork)))) / 2.04
        print d[eachNode]

    return jsonify(d)


@api.route('/whoami')
@login_required
def whothefuckami():
    return (str(g.user['id']), 200)


@api.route('/search')
def srch():
    # this shall be search algorithm for autocompletion, this shall return users with limit
    pass
