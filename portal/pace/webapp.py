#! /usr/bin/env python

from flask import Flask
from flask import render_template
from flask import Response
from flask import make_response 

# from mongoengine import *

from pace import app
import collections
from collections import OrderedDict
import operator

import json
import urllib

#Model Timing Library:
import modelTiming as mt
#modelTiming database information:
import mtDB

from pace_common import *

# Initialize database connection
connectDatabase()

UPLOAD_FOLDER='/var/www/portal/pace/upload'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'tgz', 'gz', 'tar', 'aspen'])
# Uploading file
from flask import request,redirect,url_for
from werkzeug.utils import secure_filename
import os
def stream(file_proxy, chunk = 4096): # file_proxy is of type GridFSProxy
	while True:
		next_chunk = file_proxy.read(chunk)
		if len(next_chunk) == 0:
			return
		yield next_chunk


@app.route("/")
def welcome():
	return render_template('welcome.html')

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/upload2', methods=['POST'])
def upload_file2():
	if request.method == 'POST':
		file = request.files['myfilename']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
			return '''
			<!doctype html>
			<title>Upload sucess</title>
			<h1>Upload sucess</h1>
			'''

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['myfilename']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(UPLOAD_FOLDER, filename))
			return '''
			<!doctype html>
			<title>Upload sucess</title>
			<h1>Upload sucess</h1>
			'''
			#return redirect(url_for('uploaded_file',filename=filename))
		else:
			return '''
				<!doctype html>
				<title>Error</title>
				<h1>Error uploading your file</h1>
				'''
	return render_template('upload.html')
    # return '''
    # <!doctype html>
    # <title>Upload new File</title>
    # <h1>Upload new File</h1>
    # <form action="" method=post enctype=multipart/form-data>
    #   <p><input type=file name=file>
    #      <input type=submit value=Upload>
    # </form>
    # '''	

from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


@app.errorhandler(404)
def page_not_found(error):
	return render_template('error.html'), 404	

#Model Timing web-interface.
@app.route("/mt")
def mthtml():
    return render_template("modelTiming.html")
@app.route("/mtQuery/",methods=["POST"])
def mtQuery():
    resultNodes = mtDB.paceConn.execute("select jsonVal from model_timing where expID = "+request.form['expID']+ " and extension = '"+request.form['extension']+"'").fetchall()[0].jsonVal
    return "["+resultNodes+","+json.dumps(mt.valueList[0])+"]"
