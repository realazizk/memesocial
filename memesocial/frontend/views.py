from flask import Blueprint

frontend = Blueprint(
    'frontend',
    __name__
)


@frontend.route('/')
def index():
    return 'Hello World'
