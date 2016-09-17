import sys
import json
import pytest
from peewee import OperationalError
sys.path.append('/home/pi/projects/px1/')


@pytest.fixture
def client(request):
    import memesocial
    memesocial.init('memesocial.config.testingConfig')
    client = memesocial.app.test_client()

    with memesocial.app.app_context():
        try:
            memesocial.db.drop_tables(memesocial.all_tables)
        except OperationalError:
            # This occurs when the table does not exist
            pass
        memesocial.db.create_tables(memesocial.all_tables)

    return client


def register_user(client, username, password):
    """
    test user register endopoint
    """
    response = client.post(
        '/api/register_user',
        data=json.dumps({
            'username': username,
            'password': password,
            'email': username + '@nobody.com'
        }),
        content_type='application/json')
    assert response.status_code == 200


def get_users(client):
    response = client.get('/api/user/1')
    assert response.data == ''


def do_login(client, username='mohamed', password='123'):
    """
    Just login
    """
    response = client.post(
        '/api/login',
        data=json.dumps({
            'username': username,
            'password': password
        }),
        content_type='application/json')
    return response.status_code


def do_logout(client):
    return client.get('/api/logout').status_code


def update_profile_image(client, imageName):
    response = client.post(
        '/api/update_profile_image',
        content_type='multipart/form-data',
        buffered=True,
        data={
            'file-input': (open(imageName, 'rb'), imageName)
        })
    return response.status_code


def update_cover(client, colorCode):
    response = client.get('/api/update_cover/%s' % colorCode)
    return response.status_code


def mk_content(client, imageName, description):
    response = client.post(
        '/api/create_content',
        content_type='multipart/form-data',
        buffered=True,
        data={
            'input-21': (open(imageName, 'rb'), imageName)
        })
    return (response.status_code, json.loads(response.data))


def test_hello_world(client):
    # just to test if my config works
    assert client.get('/api/hello').data == 'Hello Mohamed'


def test_auth_system(client):
    """
    test authentifcation system, login/register n logout
    """
    register_user(client, 'mohamed', '123')
    assert do_login(client) == 200
    assert do_logout(client) == 200


def test_change_images(client):
    register_user(client, 'mohamed', '123')
    do_login(client)
    assert update_cover(client, 'EC407A') == 200
    assert update_cover(client, 'FFFFFF') == 422
    assert update_profile_image(client, 'imgTest.jpg') == 200


def heart_content(client, cid):
    response = client.get('/api/heartit/%i' % cid, )
    return response.status_code


def unheart_content(client, cid):
    response = client.get('/api/unheartit/%i' % cid)
    return response.status_code


def get_content(client, cid):
    response = client.get('/api/content/%i' % cid)
    return response.status_code, json.loads(response.data)


def test_content(client):
    """
    make content heart it and unheart it test
    """

    # make new users for this
    register_user(client, 'mohamed', '123')
    register_user(client, 'gauss', 'motherfucker')
    do_login(client)
    # make content
    r = mk_content(client, 'imgTest.jpg', 'LOL')
    assert r[0] == 200
    assert 'success' in r[1]
    assert 'contentid' in r[1]['success'][0]
    cid = r[1]['success'][0]['contentid']
    assert heart_content(client, cid) == 200
    do_logout(client)

    print 'This shall be gauss'
    assert do_login(client, username='gauss', password='motherfucker') == 200

    assert client.get('/api/whoami').data == '2'

    assert heart_content(client, cid) == 200
    r = get_content(client, cid)
    assert r[0] == 200
    assert 'success' in r[1]
    print r
    assert len(r[1]['success']['hearters']) == 2

    # test unheart
    assert unheart_content(client, cid) == 200
    # test unheart already unhearted
    assert unheart_content(client, cid) == 202

    # see if unhearted ?
    r = get_content(client, cid)
    assert r[0] == 200
    assert 'success' in r[1]
    assert len(r[1]['success']['hearters']) == 1


def get_user_posts(client, userid):
    response = client.get('/api/user_posts/%i' % userid)
    return response.status_code, json.loads(response.data)

def get_news_feed(client):
    response = client.get('/api/news_feed')
    return response.status_code, json.loads(response.data)


def test_hide_content(client):
    register_user(client, 'mohamed', 'mohamed')
    register_user(client, 'user1', 'user1')
    do_follow(client, 'user1', 'user1', 1)
    do_login(client, 'mohamed', 'mohamed')
    mk_content(client, 'imgTest.jpg', 'desc')
    # hide it?
    response = client.post(
        '/api/content/1/hide',
        data=json.dumps({
            'hide': 'true'
        }),
        content_type='application/json')
    # check if hidden?
    assert response.status_code == 200
    assert json.loads(response.data).has_key('success') == True
    resp = get_content(client, 1)
    assert resp[0] == 422
    # check content hidden from user page?
    # shall be empty
    code, resp = get_user_posts(client, 1)
    assert resp['errors'][0]['detail'] == 'No more Posts'

    # check user feed
    do_logout(client)
    do_login(client, 'user1', 'user1')
    code, resp = get_news_feed(client)
    assert resp == []


def do_follow(client, user, password, target):
    do_login(client, user, password)
    assert client.get('/api/follow/%i' % target).status_code == 200
    do_logout(client)


def do_comment(client, contentId, commentContent):
    response = client.post(
        '/api/comment',
        data=json.dumps({
            'content_id': contentId,
            'comment_content': commentContent
        }),
        content_type='application/json')
    return response.status_code


def do_heart(client, username, password, cid):
    do_login(client, username=username, password=password)
    heart_content(client, cid)
    do_logout(client)


def test_comment(client):
    register_user(client, 'mohamed', '123')
    register_user(client, 'gauss', 'motherfucker')
    do_login(client, username='mohamed', password='123')
    assert mk_content(client, 'imgTest.jpg', 'Yay funny meme')[0] == 200
    do_logout(client)
    do_login(client, username='gauss', password='motherfucker')
    assert do_comment(client, 1, 'Really funny lol') == 200
    rv = get_content(client, 1)
    assert rv[0] == 200
    assert len(rv[1]['success']['commentors']) == 1

    # test of comment on content that does not exist
    assert do_comment(client, 97, 'Fuck all you') == 404


def do_content(client, username, password, imgName, desc):
    do_login(client, username=username, password=password)
    mk_content(client, imgName, desc)
    do_logout(client)


def test_network(client):
    """
    Keyword Arguments:
    client -- client callback
    What will this do is test the follow system, and test my suggestion leaders suggestion algorithms
    """
    register_user(client, 'mohamed', '123')
    register_user(client, 'gauss', 'motherfucker')
    register_user(client, 'euler', 'mathisCool')
    register_user(client, 'unke1', 'unke1')
    register_user(client, 'test1', 'test1')
    register_user(client, 'gigi1', 'pipi1')
    # this should not be in outside of the local network
    register_user(client, 'HaaHa', 'papa')
    register_user(client, 'Chacha', 'papa')

    # building a simple follow network
    do_follow(client, 'mohamed', '123', 2)
    do_follow(client, 'mohamed', '123', 3)

    do_follow(client, 'gauss', 'motherfucker', 4)

    do_follow(client, 'euler', 'mathisCool', 2)
    do_follow(client, 'euler', 'mathisCool', 1)

    do_follow(client, 'gigi1', 'pipi1', 1)
    do_follow(client, 'gigi1', 'pipi1', 3)
    do_follow(client, 'gigi1', 'pipi1', 5)

    do_follow(client, 'test1', 'test1', 1)

    # shall be outside of the network
    do_follow(client, 'HaaHa', 'papa', 8)
    do_follow(client, 'Chacha', 'papa', 7)

    do_login(client, username='mohamed', password='123')

    # my tests for now
    assert json.loads(client.get('/api/maybe_like').data) == [
        {u'username': u'unke1',
         u'image_profile': u'/images/anonymous.png',
         u'id': 4}, {u'username': u'test1',
                     u'image_profile': u'/images/anonymous.png',
                     u'id': 5}, {u'username': u'gigi1',
                                 u'image_profile': u'/images/anonymous.png',
                                 u'id': 6}
    ]


def get_feed(client):
    response = client.get('/api/news_feed')
    return response.data


def test_meme_feed(client):
    """
    Keyword Arguments:
    client -- the client callback function
    """
    register_user(client, 'mohamed', '123')
    register_user(client, 'gauss', 'motherfucker')
    register_user(client, 'euler', 'mathisCool')
    register_user(client, 'unke1', 'unke1')
    register_user(client, 'test1', 'test1')
    register_user(client, 'gigi1', 'pipi1')

    do_content(client, 'mohamed', '123', 'imgTest.jpg', 'My description')
    do_heart(client, 'gauss', 'motherfucker', 1)

    do_content(client, 'unke1', 'unke1', 'imgTest.jpg', 'My description')
    do_heart(client, 'gauss', 'motherfucker', 2)

    do_content(client, 'gauss', 'motherfucker', 'imgTest.jpg',
               'My description')
    do_heart(client, 'unke1', 'unke1', 3)

    do_follow(client, 'gauss', 'motherfucker', 1)
    do_follow(client, 'mohamed', '123', 2)
    do_follow(client, 'mohamed', '123', 3)

    do_follow(client, 'gauss', 'motherfucker', 4)

    do_follow(client, 'euler', 'mathisCool', 2)
    do_follow(client, 'euler', 'mathisCool', 1)
    do_follow(client, 'gauss', 'motherfucker', 3)

    do_follow(client, 'gigi1', 'pipi1', 1)
    do_follow(client, 'gigi1', 'pipi1', 3)
    do_follow(client, 'gigi1', 'pipi1', 5)

    do_follow(client, 'test1', 'test1', 1)

    do_login(client, 'gauss', 'motherfucker')
    l = json.loads(get_feed(client))
    k, s = l[0]['score'], l[1]['score']
    assert max(k, s) == 0.25333333333333335
    assert min(k, s) == 0.23333333333333334


def searchIt(client, searchTerm):
    """
    Keyword Arguments:
    client     --
    searchTerm -- the search Term
    """

    response = client.post(
        '/api/search',
        content_type='application/json',
        data=json.dumps({
            'searchTerm': searchTerm
        }))

    return response.status_code, json.loads(response.data)


def test_search(client):
    """
    Keyword Arguments:
    client -- Pytest fixture which is a werkzeug test_client app instance
    """

    register_user(client, 'mohamed', '123')
    register_user(client, 'mohamedR', 'motherfucker')
    register_user(client, 'euler', 'mathisCool')
    register_user(client, 'unke1', 'unke1')
    register_user(client, 'gigi2', 'test1')
    register_user(client, 'gigi1', 'pipi1')

    # test search term length < 4
    rsp = searchIt(client, 'mo')
    assert rsp[0] == 422
    assert rsp[1][
        'error'] == 'You shall send a term which length is more than 4.'

    # test search for persons
    rsp = searchIt(client, 'mohamed')
    assert rsp[0] == 200
    assert len(rsp[1]['persons']) == 2

    # test search of person not found
    rsp = searchIt(client, 'noting')
    assert rsp[0] == 200
    assert len(rsp[1]['persons']) == 0
