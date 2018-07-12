#! /usr/bin/env python

from flask import Flask
from flask import render_template
from flask import Response
from flask import make_response 
from flask import send_from_directory
from collections import OrderedDict
from pace import app

import sys 
import collections
import operator
import json
import urllib

# Destination and allowed file extention
UPLOAD_FOLDER='/pace/dev1/portal/upload'
ALLOWED_EXTENSIONS = set(['txt','csv', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'tgz', 'gz', 'tar', 'aspen'])

# Uploading file
from flask import request,redirect,url_for
from werkzeug.utils import secure_filename
import os

# Limit file size
def stream(file_proxy, chunk = 4096): # file_proxy is of type GridFSProxy
	while True:
		next_chunk = file_proxy.read(chunk)
		if len(next_chunk) == 0:
			return
		yield next_chunk

# Home page
@app.route("/")
def welcome():
	return render_template('welcome.html')

# Check file extention
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Store file in server
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			#sys.stderr.write('inside allowed file')
			filename = secure_filename(file.filename)
			file.save(os.path.join(UPLOAD_FOLDER, filename))
			return('File Upload Success')
		else:
			return ('Error Uploading file, Try again')
	return render_template('upload.html')
 	


# Error handler
@app.errorhandler(404)
def page_not_found(error):
	return render_template('error.html'), 404	

