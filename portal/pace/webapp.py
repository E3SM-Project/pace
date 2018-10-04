#! /usr/bin/env python

from flask import Flask,render_template,Response,make_response,send_from_directory,request,redirect,url_for
from collections import OrderedDict
from pace import app
import parse as parse
import sys 
import collections
import operator
import json
import urllib
from sqlalchemy.orm import sessionmaker
from __init__ import db

#Model Timing Library:
import modelTiming as mt
#modelTiming database information:
from pace_common import *

UPLOAD_FOLDER='/pace/prod/portal/upload'
#UPLOAD_FOLDER='/pace/dev1/portal/upload'
ALLOWED_EXTENSIONS = set(['zip', 'tgz', 'gz', 'tar','txt'])

# Uploading file
from werkzeug.utils import secure_filename
import os
from datastructs import *

# Home page
@app.route("/")
def homePage():
    return searchPage("*",True)

@app.route("/about")
def aboutPage():
    return render_template("about.html")

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
			filename = secure_filename(file.filename)
			file.save(os.path.join(UPLOAD_FOLDER, filename))
			return(parse.parseData())
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
@app.route("/summary/<expID>/<rank>/<compare>/<threads>/")
@app.route("/summary/<expID>/<rank>/<compare>/")
@app.route("/summary/<expID>/<rank>/")
def summaryHtml(expID,rank,compare="",threads=""):
    ids = expID.split(",")
    ranks = rank.split(",")
    resultString = ""
    extraStr = ""
    for i in range(len(ids)):
        if i > 0:
            resultString+=","
        resultString+="['"+ids[i]+"','"+ranks[i]+"']"
    if compare == "compare":
        extraStr = "var compare = true;"
    if (not threads == "") or ( (not compare == "") and not compare == "compare"):
        rankStr=""
        if(not compare == "compare"):
            threadStr = compare
        else:
            threadStr = threads
        extraStr+="threadList = "+json.dumps(threadStr.split(","))+";"
            

    return render_template("modelTiming.html",exp = "var expData = ["+resultString+"];"+extraStr)

@app.route("/summaryQuery/<expID>/<rank>/",methods=["GET"])
def summaryQuery(expID,rank):
    resultNodes=""
    listIndex = 0
    if expID == "-1":
        resultNodes = mt.parse("/pace/assets/static/samples/model_timing.0000.new")
    elif expID == "-2":
        resultNodes = mt.parse("/pace/assets/static/samples/model_timing_stats")
    else:
        resultNodes = db.engine.execute("select jsonVal from model_timing where expid = "+expID+ " and rank = '"+rank+"'").fetchall()[0].jsonVal
    if rank == 'stats':
        listIndex = 1
        #Grab processes > 1 second:
        nodeTemp = json.loads(resultNodes)
        newJson = []
        for node in nodeTemp[0]:
            if node["values"]["wallmax"] > 0:
                newJson.append(node)
        #Sort from least to greatest:
        for i in range(len(newJson)):
            for j in range(len(newJson)):
                if(newJson[j]["values"]["wallmax"] < newJson[i]["values"]["wallmax"]):
                    temp = newJson[i]
                    newJson[i] = newJson[j]
                    newJson[j] = temp
        #Grab the top twenty nodes:
        while not len(newJson) == 50:
            newJson.pop()
        resultNodes = "["+json.dumps(newJson)+"]"
    return "["+resultNodes+","+json.dumps(mt.valueList[listIndex])+",\""+expID+"\",\""+rank+"\"]"

@app.route("/exps")
def expsList():
    myexps = []
    # initDatabase()
    myexps = db.session.query(Timingprofile).order_by(Timingprofile.expid.desc()).limit(20)
    # myexps = Timingprofile.query.order_by(Timingprofile.expid.asc()).limit(25)
    return render_template('exps.html', explist = myexps)

@app.route("/search/")
@app.route("/search/<searchQuery>")
def searchPage(searchQuery="*",isHomepage=False):
    homePageStr = ""
    if isHomepage:
        homePageStr = "var homePage = true;"
    return render_template("search.html",sq = "var searchQuery = '"+searchQuery+"';",homePageStr = homePageStr)

@app.route("/exp-details/<mexpid>")
def expDetails(mexpid):
    myexp = 0
    myexp = db.session.query(Timingprofile).filter_by(expid = mexpid).all()[0]
    mypelayout = db.session.query(Pelayout).filter_by(expid = mexpid).all()[0]
    myruntime = db.session.query(Runtime).filter_by(expid = mexpid).all()[0]
    return render_template('exp-details.html', exp = myexp, pelayout = mypelayout, runtime = myruntime)

EXPS_PER_RQ=20
@app.route("/ajax/exps/<int:pageNum>")
def expsAjax(pageNum):
    numexps = db.session.query(Timingprofile).count()
    myexps = db.session.query(Timingprofile).order_by(Timingprofile.expid.desc())[pageNum * EXPS_PER_RQ : (pageNum + 1) * EXPS_PER_RQ]
    pruned_data = {"numRows": numexps, "data": []}
    for exp in myexps:
	# var row = [o.expid,o.user,o.machine,o.total_pes_active,o.run_length,o.model_throughput,o.mpi_tasks_per_node,o.compset,o.grid];
        pruned_data["data"].append({"expid": exp.expid, "user": exp.user, "machine": exp.machine, "total_pes_active": exp.total_pes_active, "run_length": exp.run_length, "model_throughput": exp.model_throughput, "mpi_tasks_per_node": str(exp.mpi_tasks_per_node), "compset": exp.compset, "grid": exp.grid})
    return make_response(json.dumps(pruned_data))

@app.route("/ajax/search/<searchTerms>")
@app.route("/ajax/search/<searchTerms>/<limit>")
@app.route("/ajax/search/<searchTerms>/<limit>/<matchAll>")
def searchBar(searchTerms,limit = False,matchAll = False):
    resultItems = []
    filteredItems = []
    variableList = ["user","expid","machine","total_pes_active","run_length","model_throughput","mpi_tasks_per_node","compset","exp_date"]
    termList = []
    if searchTerms == "*":
        queryStr = "select "+str(variableList).strip("[]").replace("'","")+" from timingprofile order by expid desc"
        if limit:
            queryStr+=" limit "+limit
        allResults = db.engine.execute(queryStr).fetchall()
        for result in allResults:
            resultItems.append(result)
        #Replacement for filtered items loop:
        for item in resultItems:
            resultDict = {}
            for key in item.keys():
                if 'Decimal' in str(item[key]):
                    resultDict[key] = str(item[key].precision)
                else:
                    resultDict[key] = str(item[key])
            filteredItems.append(resultDict)

    elif matchAll == "matchall":
        #We assume the user is typing information with the following format: "user:name machine:titan etc:etc"
        for word in searchTerms.split("+"):
            termList.append(word.replace(";","").replace("\\c",""))
        #Make a list of compiled variables to query in one swoop:
        strList = []
        for element in termList:
            syntax = element.split(":")
            if syntax[0] in variableList:
                strList.append(syntax[0]+' like "%%'+syntax[1]+'%%"')
        compiledString = "select " + str(variableList).strip("[]").replace("'","") + " from timingprofile where "
        for i in range(len(strList)):
            compiledString+=strList[i]
            if not i==len(strList) - 1:
                compiledString+=" and "
        compiledString+=" order by expid desc limit "+limit+";"
        #Copy/paste from above:
        allResults = db.engine.execute(compiledString).fetchall()
        for result in allResults:
            resultItems.append(result)
        #Replacement for filtered items loop:
        for item in resultItems:
            resultDict = {}
            for key in item.keys():
                if 'Decimal' in str(item[key]):
                    resultDict[key] = str(item[key].precision)
                else:
                    resultDict[key] = str(item[key])
            filteredItems.append(resultDict)

    else:
        for word in searchTerms.split("+"):
            termList.append(word.replace(";","").replace("\\c",""))
        for word in variableList:
            queryStr = "select " + str(variableList).strip("[]").replace("'","") + " from timingprofile where "+word+" like "
            firstValue = True
            for term in termList:
                if not firstValue:
                    queryStr+=" or "+word+" like "
                queryStr+='"%%'+term+'%%"'
                firstValue = False
            queryStr+=" order by expid desc"
            if limit:
                queryStr+=" limit "+limit
            resultItems.append(db.engine.execute(queryStr).fetchall())
        #Filter out duplicates:
        for query in resultItems:
            for element in query:
                unique = True
                for item in filteredItems:
                    if element.user == item["user"] and element.expid == item["expid"] and element.machine == item["machine"]:
                        unique = False
                        break
                if unique:
                    resultDict = {}
                    for key in element.keys():
                        if 'Decimal' in str(element[key]):
                            resultDict[key] = str(element[key].precision)
                        else:
                            resultDict[key] = str(element[key])
                    filteredItems.append(resultDict)
    #Grab the ranks based of of filteredItems:
    rankList = []
    for item in filteredItems:
        itemRanks = []
        queryResults = db.engine.execute("select rank from model_timing where expid = "+str(item["expid"])).fetchall()
        for result in queryResults:
            itemRanks.append(result.rank)
        rankList.append([itemRanks,[]]) 
    return json.dumps([filteredItems,rankList])

#Get a specific list of elements from timingprofile. Only specific elements are allowed, so users cannot grab everything.
@app.route("/ajax/getDistinct/<entry>")
def getMachines(entry):
    queryList = []
    if entry in ["machine","user"]:
        distQuery = db.engine.execute("select distinct "+entry+" from timingprofile").fetchall()
        for element in distQuery:
            queryList.append(element[entry])
    return json.dumps(queryList)

@app.route("/platforms/<platform>/")
def platformsRedirect(platform):
    return searchPage(platform)

@app.route("/users/<user>/")
def usersRedirect(user):
    return searchPage(user)
