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

#Model Timing Library:
import modelTiming as mt
#modelTiming database information:
import mtDB

from pace_common import *

# Initialize database connection
connectDatabase()

UPLOAD_FOLDER='/pace/prod/portal/upload'
ALLOWED_EXTENSIONS = set(['zip', 'tgz', 'gz', 'tar','txt'])

# Uploading file
from flask import request,redirect,url_for
from werkzeug.utils import secure_filename
import os

app.config['MAX_CONTENT_LENGTH'] = 128 * 1024 * 1024

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
			os.system("/opt/venv/pace/bin/python /pace/dev1/portal/upload/parse.py")
			return('File Upload and Store in Database Success')
		else:
			return ('Error Uploading file, Try again')
	return render_template('upload.html')
 	
@app.route("/uploadlogin", methods=['GET','POST'])
def uploadlogin():
	if request.method == 'POST':
		admin = request.form['name']
		admin_pass = request.form['pass']
		a=admin+admin_pass
		z=int(len(a))
		b=''
		for i in range(z):
			b = b + chr(ord(a[i]) + 2)
		c=b+a
		y=int(len(c))
		d=''
		for i in range(y):
			d = d + chr(ord(c[i])+1)			
		f=open('/pace/dev1/portal/pace/pass.txt','r')
		for line in f:
			admin = line.split(None,1)[0]
			print(admin)
			if admin==d:
				return("ok")				
				
		return("not")

# Error handler
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

