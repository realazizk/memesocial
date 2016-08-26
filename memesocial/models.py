
from peewee import SqliteDatabase, Model,\
    PrimaryKeyField, FixedCharField, ForeignKeyField,\
    BooleanField, TextField, DateTimeField

__author__ = "Mohamed Aziz Knani"

__doc__ = """
 My models file, please see database_design.erd
"""

db = SqliteDatabase('my_app.db')


class BaseModel(Model):

    class Meta:
        database = db


class Language(BaseModel):
    id = PrimaryKeyField()
    name = FixedCharField(100)


class User(BaseModel):
    id = PrimaryKeyField()
    username = FixedCharField(100)
    password = FixedCharField(100)
    imageProfile = FixedCharField(250)
    coverProfile = FixedCharField(250)
    email = FixedCharField(100)
    langid = ForeignKeyField(Language, related_name='id')
    active = BooleanField()
    online = BooleanField()


class Block(BaseModel):
    id = PrimaryKeyField()
    user = ForeignKeyField(User, related_name='id')
    blockedUser = ForeignKeyField(User, related_name='id')


class Image(BaseModel):
    id = PrimaryKeyField()
    url = FixedCharField(250)
    owner = ForeignKeyField(User, related_name='id')
    description = TextField()
    date = DateTimeField()


class Comment(BaseModel):
    id = PrimaryKeyField()
    body = TextField()
    date = DateTimeField()
    imageId = ForeignKeyField(Image, related_name='id')


class Connection(BaseModel):
    id = PrimaryKeyField()
    date = DateTimeField()
    userId = ForeignKeyField(User, related_name='id')
    ip = FixedCharField(20)
    useragent = FixedCharField(200)


class FollowerRelation(BaseModel):
    id = PrimaryKeyField()
    follower = ForeignKeyField(User, related_name='id')
    leader = ForeignKeyField(User, related_name='id')


class Heart(BaseModel):
    id = PrimaryKeyField()
    imageId = ForeignKeyField(Image, related_name='id')
    userId = ForeignKeyField(User, related_name='id')
