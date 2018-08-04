#! /usr/bin/env python

from flask import Flask
from flask import render_template
from flask import Response
from flask import make_response 
from flask import send_from_directory
from collections import OrderedDict
from pace import app
import parse as parse
import sys 
import collections
import operator
import json
import urllib

#Model Timing Library:
import modelTiming as mt
#modelTiming database information:

from pace_common import *

UPLOAD_FOLDER='/pace/prod/portal/upload'
#UPLOAD_FOLDER='/pace/dev1/portal/upload'
ALLOWED_EXTENSIONS = set(['zip', 'tgz', 'gz', 'tar','txt'])

# Uploading file
from flask import request,redirect,url_for
from werkzeug.utils import secure_filename
import os

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
			#os.system("/opt/venv/pace/bin/python /pace/prod/portal/pace/parse.py")
			parse.parseData()
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
@app.route("/mt",methods=["POST","GET"])
def mthtml():
    expData = ""
    if len(request.form) > 0:
        expData = "var expData = '"+request.form["exp"]+"';"
    return render_template("modelTiming.html",exp = expData)

@app.route("/mtQuery/",methods=["POST"])
def mtQuery():
    resultNodes=""
    if len(request.form) > 0 and request.form["expID"] == "-1":
        resultNodes = mt.parse("/pace/assets/static/model_timing.0000.new")
    else:
        resultNodes = dbConn.execute("select jsonVal from model_timing where expID = "+request.form['expID']+ " and rank = '"+request.form['rank']+"'").fetchall()[0].jsonVal
    return "["+resultNodes+","+json.dumps(mt.valueList[0])+"]"

@app.route("/exps2")
def experiments():
    #Convert table elements into dictionaries:
    def queryConvert(expQuery):
        resultList = []
        for element in expQuery:
            elementTuple = element.items()
            resultListElement = {}
            for key in elementTuple:
                resultListElement[key[0]] = key[1]
            resultList.append(resultListElement)
        return resultList
    try:
        expSelection = queryConvert(dbConn.execute("select lid,expID from timing_profile").fetchall())
        expExtensions = queryConvert(dbConn.execute("select expID,rank from model_timing").fetchall())
        return render_template("experiments.html",expS = "var experiments="+json.dumps(expSelection),expE = "var extensions="+json.dumps(expExtensions))
    except:
        #run the failsafe, which basically returns nothing... If this happens, we will read placeholder data by file.
        return render_template("experiments.html")


@app.route("/exps")
def expsList():
    myexps = []
    myexps = dbSession.query(Timingprofile).order_by(Timingprofile.expid.desc()).limit(10)
    return render_template('exps.html', explist = myexps)


