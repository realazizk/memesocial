

# simple functions that I shall be using more than once
from base64 import b64decode
from memesocial import config
import imghdr
import os
import shutil
import uuid
import urllib
import StringIO
import urlparse


def allowed_file(extension):
    return extension in config.ALLOWED_EXTENSIONS


def decode_image(imageData):
    return b64decode(imageData)


def save_file(fileData):
    filename = str(uuid.uuid4())
    bufferd = StringIO.StringIO(fileData)
    ext = imghdr.what(bufferd)
    if allowed_file(ext):
        finalFileName = filename + '.' + ext
        with open(os.path.join(config.UPLOAD_FOLDER, finalFileName), 'wb') as myfile:
            shutil.copyfileobj(bufferd, myfile)
    return finalFileName


def form_url(baseUrl, parms):
    return urlparse.urljoin(baseUrl[0], baseUrl[1]) + '?' + urllib.urlencode(parms)
