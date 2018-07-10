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


@app.errorhandler(404)
def page_not_found(error):
	return render_template('error.html'), 404	

@app.route("/login", methods=['GET','POST'])
def login():
	if request.method == 'POST':
		admin = request.form['admin']
		admin_pass = request.form['admin_pass']
		return(admin)
