from os import environ
import tempfile
DEBUG = True
TESTING = True
SECRET_KEY = "myTopSecretKey"
PLUS_CLIENT_ID = '277809981459-v1buepo73pneahp7p7gmrdbkfhmi5m4g.apps.googleusercontent.com'
PLUS_CLIENT_SECRET = 'K_P9lEWiLSBiAn6_gczl48Vf'
UPLOAD_FOLDER = '/home/pi/projects/px1/images/'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
SITE_URL = 'http://localhost:1337'
# XXX: FOR DEBUGGING
DATABASE = 'application.db'
if environ.get('TESTING') == '1':
    DATABASE = tempfile.mkstemp()[1]
