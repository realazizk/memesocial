from peewee import MySQLDatabase, SqliteDatabase
import os

# create images directory if it does not exist
if not os.path.exists(os.path.join(os.getcwd(), 'images')):
    os.makedirs(os.path.join(os.getcwd(), 'images'))


# my base config which is a shared class
class baseConfig(object):
    SECRET_KEY = "myTopSecretKey"
    PLUS_CLIENT_ID = '277809981459-v1buepo73pneahp7p7gmrdbkfhmi5m4g.apps.googleusercontent.com'
    PLUS_CLIENT_SECRET = 'K_P9lEWiLSBiAn6_gczl48Vf'
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'images')

    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    SITE_URL = 'http://localhost:1337'
    PROFILE = True
    THUMBNAIL_SIZE = (128, 128)


# The dev config using sqlite?
class devConfig(baseConfig):
    SECRET_KEY = "myTopSecretKey"
    DEBUG = True
    TESTING = True
    # Using a sqlite database for development
    DATABASE_OBJECT = SqliteDatabase(
        'database.db'
    )


# The config for testing the application?
class testingConfig(baseConfig):
    # If DEBUG is true it causes some errors while testing.
    DEBUG = False
    TESTING = True

    # an in memory database?
    DATABASE_OBJECT = SqliteDatabase(
        ':memory:'
    )


# The config for production server
class productionConfig(baseConfig):
    # using a mysql database
    DATABASE_OBJECT = MySQLDatabase(
        'memesocialDatabase', user='root', password='123', host='127.0.0.1')

    DEBUG = False
    TESTING = False
    SECRET_KEY = 'IMPORTANT_CONFIGURE_THIS!'
    SITE_URL = 'http://memesocial.com'
