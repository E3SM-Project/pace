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
			return(parse.parseData())
			#return('File Upload and Store in Database Success')
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
    resultName="failsafe file"
    listIndex = 0
    if expID == "-1":
        resultNodes = mt.parse("/pace/assets/static/model_timing.0000.new")
    else:
        resultNodes = dbConn.execute("select jsonVal from model_timing where expid = "+expID+ " and rank = '"+rank+"'").fetchall()[0].jsonVal
        resultName = dbConn.execute("select expid from timing_profile where expid = "+expID).fetchall()[0].expid
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
    return "["+resultNodes+","+json.dumps(mt.valueList[listIndex])+",\""+str(resultName)+"\",\""+rank+"\"]"

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
        initDatabase()
        # dbSession = dbSessionf()
        # expSelection = queryConvert(dbSession.query(Timingprofile).	
        expSelection = queryConvert(dbConn.execute("select lid,expID from timing_profile").fetchall())
        expExtensions = queryConvert(dbConn.execute("select expID,rank from model_timing").fetchall())
        return render_template("experiments.html",expS = "var experiments="+json.dumps(expSelection),expE = "var extensions="+json.dumps(expExtensions))
    except:
        #run the failsafe, which basically returns nothing... If this happens, we will read placeholder data by file.
        return render_template("experiments.html")


@app.route("/exps")
def expsList():
    myexps = []
    # initDatabase()
    dbSession = dbSessionf()
    myexps = dbSession.query(Timingprofile).order_by(Timingprofile.expid.desc()).limit(20)
    # myexps = Timingprofile.query.order_by(Timingprofile.expid.asc()).limit(25)
    dbSession.close()
    return render_template('exps.html', explist = myexps)

@app.route("/exp-details/<mexpid>")
def expDetails(mexpid):
    myexp = 0
    dbSession = dbSessionf()
    myexp = dbSession.query(Timingprofile).filter_by(expid = mexpid).all()[0]
    mypelayout = dbSession.query(Pelayout).filter_by(expid = mexpid).all()[0]
    myruntime = dbSession.query(Runtime).filter_by(expid = mexpid).all()[0]
    dbSession.close()
    return render_template('exp-details.html', exp = myexp, pelayout = mypelayout, runtime = myruntime)

EXPS_PER_RQ=20
@app.route("/ajax/exps/<int:pageNum>")
def expsAjax(pageNum):
    dbSession = dbSessionf()
    numexps = dbSession.query(Timingprofile).count()
    myexps = dbSession.query(Timingprofile).order_by(Timingprofile.expid.desc())[pageNum * EXPS_PER_RQ : (pageNum + 1) * EXPS_PER_RQ]
    pruned_data = {"numRows": numexps, "data": []}
    for exp in myexps:
	# var row = [o.expid,o.user,o.machine,o.total_pes_active,o.run_length,o.model_throughput,o.mpi_tasks_per_node,o.compset,o.grid];
        pruned_data["data"].append({"expid": exp.expid, "user": exp.user, "machine": exp.machine, "total_pes_active": exp.total_pes_active, "run_length": exp.run_length, "model_throughput": exp.model_throughput, "mpi_tasks_per_node": str(exp.mpi_tasks_per_node), "compset": exp.compset, "grid": exp.grid})
    dbSession.close()
    return make_response(json.dumps(pruned_data))

@app.route("/ajax/search/<searchTerms>")
@app.route("/ajax/search/<searchTerms>/<limit>")
def searchBar(searchTerms,limit = False):
    termList = []
    for word in searchTerms.split("+"):
        termList.append(word.replace(";","").replace("\\c",""))
    resultItems = []
    filteredItems = []
    variableList = ["user","expid","machine"]
    for word in variableList:
        queryStr = "select "
        firstValue = True
        for value in variableList:
            if not firstValue:
                queryStr+=","
            queryStr+=value
            firstValue = False
        queryStr+=" from timing_profile where "+word+" in ("
        firstValue = True
        for term in termList:
            if not firstValue:
                queryStr+=","
            queryStr+='"'+term+'"'
            firstValue = False
        queryStr+=")"
        if limit:
            queryStr+=" limit "+limit
        resultItems.append(dbConn.execute(queryStr).fetchall())
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
        queryResults = dbConn.execute("select rank from model_timing where expid = "+str(item["expid"])).fetchall()
        for result in queryResults:
            itemRanks.append(result.rank)
        rankList.append([itemRanks,[]])
        
    return json.dumps([filteredItems,rankList])
