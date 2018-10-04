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

#Runtime image generator: by donahue5 (Modified for use on PACE)
import pe_layout_timings as runtimeSvg

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
    basePath = "/pace/"
    if os.getenv("PACE_DOCKER_INSTANCE") == "1":
        basePath+="portal/pace/"
    else:
        basePath+="assets/"
    basePath+="static/samples"
    if expID == "-1":
        resultNodes = mt.parse(basePath+"model_timing.0000.new")
    elif expID == "-2":
        resultNodes = mt.parse(basePath+"model_timing_stats")
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
    myexp = None
    myexp = db.session.query(Timingprofile).filter_by(expid = mexpid).all()[0]
    mypelayout = db.session.query(Pelayout).filter_by(expid = mexpid).all()[0]
    myruntime = db.session.query(Runtime).filter_by(expid = mexpid).all()
    ranks = db.session.query(ModelTiming.rank).filter_by(expid = mexpid)
    return render_template('exp-details.html', exp = myexp, pelayout = mypelayout, runtime = myruntime,expid = mexpid,ranks = ranks)

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
    variableList = ["user","expid","machine","total_pes_active","run_length","model_throughput","mpi_tasks_per_node","compset","curr_date"]
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
                resultDict[key] = item[key]
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
                resultDict[key] = item[key]
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
                        resultDict[key] = element[key]
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
def getDistinct(entry):
    queryList = []
    if entry in ["machine","user"]:
        distQuery = db.engine.execute("select distinct "+entry+" from timingprofile order by "+entry).fetchall()
        for element in distQuery:
            queryList.append(element[entry])
    return json.dumps(queryList)

@app.route("/platforms/<platform>/")
def platformsRedirect(platform):
    return searchPage(platform)

@app.route("/users/<user>/")
def usersRedirect(user):
    return searchPage(user)

#A function to compare two things in alphabetical order. If word1 should be earlier alphabetized, return true.
def charCompare(word1,word2):
    maxCount = None
    if len(word1) > len(word2):
        maxCount = len(word2)
    else:
        maxCount = len(word1)
    for i in range(maxCount):
        if word1[i] < word2[i]:
            return True
    return False
#This is designed for the search bar on the website. It predicts what a user may be looking for based on where the dev specifies to search.
@app.route("/ajax/similarDistinct/<keyword>")
def searchPrediction(keyword):
    #The keyword is designed to be a single word without any potential database loopholes:
    keyword = keyword.replace("\\c","").replace(";","").replace(" ","")
    #Grab elements based on these columns:
    columnNames = ["user","machine","expid"]
    resultWords = []
    for column in columnNames:
        distQuery = db.engine.execute("select distinct "+column+" from timingprofile where "+column+" like '%%"+keyword+"%%' limit 20").fetchall()
        for element in distQuery:
            resultWords.append(str(element[column]))
    #Sort them by similar name:
    for i in range(len(resultWords)):
        if keyword[0] == resultWords[i][0]:
            for j in range(len(resultWords)):
                print(j)
                # or charCompare(resultWords[i],resultWords[j]
                if not keyword[0] == resultWords[j][0]:
                    temp = resultWords[j]
                    resultWords[j] = resultWords[i]
                    resultWords[i]=temp
                    break
    return json.dumps(resultWords)

@app.route("/svg/runtime/<expid>")
def getRuntimeSvg(expid):
    resultElement = {}
    try:
        runtimeQuery = db.session.query(Runtime).filter_by(expid = int(expid)).all()
        for element in runtimeQuery:
            resultElement[element.component] = {"seconds":element.seconds,"model_years":element.model_years,"model_day":element.model_day}
        for key in resultElement.keys():
            peQuery = db.session.query(Pelayout.root_pe,Pelayout.tasks).filter(Pelayout.expid == int(expid),Pelayout.component.ilike("%"+key+"%")).all()
            if len(peQuery) > 0:
                resultElement[key]["root_pe"] = peQuery[0].root_pe
                resultElement[key]["tasks"] = peQuery[0].tasks -1
    except ValueError:
        return render_template("error.html"),404
    return Response(runtimeSvg.render(resultElement).read(),mimetype="image/svg+xml")