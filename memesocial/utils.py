

# simple functions that I shall be using more than once
from base64 import b64decode
import imghdr
import os
import shutil
import uuid
import urllib
import StringIO
import urlparse
import re
from memesocial import app

config = app.config
MENTION_MATCH = re.compile('\B@(\w*)')


def allowed_file(extension):
    return extension in config['ALLOWED_EXTENSIONS']


def decode_image(imageData):
    return b64decode(imageData)


def save_file(fileData):
    filename = str(uuid.uuid4())
    bufferd = StringIO.StringIO(fileData)
    ext = imghdr.what(bufferd)
    if allowed_file(ext):
        finalFileName = filename + '.' + ext
        with open(os.path.join(config['UPLOAD_FOLDER'], finalFileName), 'wb') as myfile:
            shutil.copyfileobj(bufferd, myfile)
    return finalFileName


def form_url(baseUrl, parms):
    return urlparse.urljoin(baseUrl[0], baseUrl[1]) + '?' + urllib.urlencode(parms)


def get_mentions(text):
    """
    Returns mentioned users.
    text -- the input text
    """
    return MENTION_MATCH.findall(text)


def tokenize(text, d):
    """
    Simple tokenizer function?
    Keyword Arguments:
    text -- The input text
    """

    def callable(match):
        try:
            return "<a class='mentions' href='%s/profile/%s'>@%s</a>" % (config['SITE_URL'], d[match.group(1)], match.group(1))
        except KeyError:
            # hmm mentioned user that does not exist return the whole match
            return match.group(0)

    return MENTION_MATCH.sub(callable, text)
