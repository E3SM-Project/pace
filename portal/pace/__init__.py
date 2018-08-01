#! /usr/bin/env python

from flask import Flask
from flask import render_template

# Import the fixer
from werkzeug.contrib.fixers import ProxyFix

# Uploading file
from flask import request,redirect,url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = '/pace/prod/portal/uploads'

app = Flask(__name__)
# Use the fixer
app.wsgi_app = ProxyFix(app.wsgi_app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Limit payload to 32 MB
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024
app.secret_key = 'p\xcb\xd8\x81z\xa5)D\x14(\x8dJ\nvjdb\x82\x9a\x8dH\rg='

if __name__ == "__main__":
	app.run(debug=True)

# Import the rest of the application logic from webapp.py
# Both of the following options work
# Circular import is okay in this case - see http://flask.pocoo.org/docs/patterns/packages/
import pace.webapp
# from webapp import *
