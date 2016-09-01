from flask import Blueprint, render_template, send_from_directory, abort
import os

frontend = Blueprint(
    'frontend',
    __name__,
    template_folder='templates'
)


@frontend.route('/static/<dire>/<filename>')
def serve_static(dire, filename):
    """
    this endpoint serves the static files in static
    """
    if dire not in set(['js', 'fonts', 'css', 'imgs']):
        abort(404)
    root_dir = os.path.dirname(os.path.realpath(__file__))
    return send_from_directory(os.path.join(root_dir, 'static', dire), filename)


@frontend.route('/')
def index():
    return render_template('index.jhtml')
