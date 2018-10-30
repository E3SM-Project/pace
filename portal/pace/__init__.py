#! /usr/bin/env python

from flask import Flask
#from flask import render_template
from pace_common import *
from flask_sqlalchemy import SQLAlchemy

# Import the fixer
from werkzeug.contrib.fixers import ProxyFix

# Uploading file
#from flask import request,redirect,url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
# Use the fixer
app.wsgi_app = ProxyFix(app.wsgi_app)

app.config['SQLALCHEMY_DATABASE_URI'] = initDatabase()
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_POOL_RECYCLE']=499
# Sarat: increasing pool size and overflow to 20
# to avoid 'TimeoutError: QueuePool limit of size 10 overflow 10 reached'
app.config['SQLALCHEMY_POOL_SIZE']=20
app.config['SQLALCHEMY_MAX_OVERFLOW']=20
db = SQLAlchemy(app)


app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Limit payload to 16 GB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024 * 16
app.secret_key = 'p\xcb\xd8\x81z\xa5)D\x14(\x8dJ\nvjdb\x82\x9a\x8dH\rg='

# Import the rest of the application logic from webapp.py
# Both of the following options work
# Circular import is okay in this case - see http://flask.pocoo.org/docs/patterns/packages/
# import pace.webapp
if __name__ == "__main__":
	app.run()
from webapp import *
