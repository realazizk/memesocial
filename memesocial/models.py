
from peewee import MySQLDatabase, Model,\
    PrimaryKeyField, FixedCharField, ForeignKeyField,\
    BooleanField, TextField, DateTimeField
from passlib.apps import custom_app_context as pwd_context


__author__ = "Mohamed Aziz Knani"

__doc__ = """
 My models file, please see database_design.erd
"""

db = MySQLDatabase('memesocialDatabase', user='root', password='123', host='127.0.0.1')


class BaseModel(Model):

    class Meta:
        database = db


class Language(BaseModel):
    id = PrimaryKeyField()
    name = FixedCharField(100)


class User(BaseModel):
    id = PrimaryKeyField()
    username = FixedCharField(100, unique=True)
    password = FixedCharField(120)

    bio = FixedCharField(100, default='')
    imageProfile = FixedCharField(250, null=True, default='/images/anonymous.png')

    # this will be some color.
    coverProfile = FixedCharField(250, null=True, default='GREEN')
    email = FixedCharField(100, null=True)
    langid = ForeignKeyField(Language, to_field='id', null=True)
    active = BooleanField()
    online = BooleanField()

    @staticmethod
    def hash_password(password):
        return pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password)


class Block(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, to_field='id', related_name='user')
    blockedUser = ForeignKeyField(
        User, to_field='id', related_name='blocked_user')


class Image(BaseModel):
    id = PrimaryKeyField()
    url = FixedCharField(250)
    owner = ForeignKeyField(User, to_field='id')
    description = TextField(null=True, default='Add a description here')
    date = DateTimeField()


class Comment(BaseModel):
    id = PrimaryKeyField()
    body = TextField()
    date = DateTimeField()
    usrId = ForeignKeyField(User, to_field='id')
    imageId = ForeignKeyField(Image, to_field='id')


class Connection(BaseModel):
    id = PrimaryKeyField()
    date = DateTimeField()
    userId = ForeignKeyField(User, to_field='id')
    ip = FixedCharField(20)
    useragent = FixedCharField(200)


class FollowerRelation(BaseModel):
    id = PrimaryKeyField()
    follower = ForeignKeyField(User, to_field='id', related_name='follower')
    leader = ForeignKeyField(User, to_field='id', related_name='leader')

    class Meta:
        # only one direct relation exists between two users.
        indexes = ((("follower", "leader"), True),)


class Heart(BaseModel):
    id = PrimaryKeyField()
    imageId = ForeignKeyField(Image, to_field='id')
    userId = ForeignKeyField(User, to_field='id')

    class Meta:
        # a user can put only one heart on a certain image
        indexes = ((("imageId", "userId"), True),)


all_tables = [Language, User, Block, Image,
              Comment, Connection, FollowerRelation, Heart]
