from flask_testing import TestCase
import flask
import sys
import json
import pytest
import tempfile
import os
sys.path.append('/home/pi/projects/px1/')
import memesocial


@pytest.fixture
def client(request):
    client = memesocial.app.test_client()

    # def teardown():
    #     """Get rid of the database again after each test."""
    #     os.close(db_fd)
    #     os.unlink(memesocial.app.config['DATABASE'])

    # request.addfinalizer(teardown)
    return client


def test_hello_world(client):
    # just to test if my config works
    assert client.get('/api/hello').data == 'Hello Mohamed'


def register_user(client, username, password):
    """
    test user register endopoint
    """
    response = client.post(
        '/api/register_user',
        data=json.dumps({
            'username': username,
            'password': password
        }),
        content_type='application/json'
    )
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
        content_type='application/json'
    )
    return response.status_code


def do_logout(client):
    return client.get('/api/logout').status_code


def test_auth_system(client):
    """
    test authentifcation system, login/register n logout
    """
    register_user(client, 'mohamed', '123')
    assert do_login(client) == 200
    assert do_logout(client) == 200
