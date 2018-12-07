#! /usr/bin/env python

from flask import Flask,render_template,Response,make_response,send_from_directory,request,redirect,url_for, session
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
import os, shutil, distutils
import re

#Model Timing Library:
import modelTiming as mt
#modelTiming database information:
from pace_common import *

from sqlalchemy.exc import SQLAlchemyError
#github imports
import binascii
from rauth import OAuth2Service

GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET = getGithubkey()

github = OAuth2Service(
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    name='github',
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    base_url='https://api.github.com/')


ALLOWED_EXTENSIONS = set(['zip', 'tgz', 'gz', 'tar','txt'])

# Uploading file
from werkzeug.utils import secure_filename
import os
from datastructs import *

#Runtime image generator: by donahue5 (Modified for use on PACE)
import pe_layout_timings as runtimeSvg

#This is for querying colors:
from matplotlib.colors import to_rgb,to_hex
import matplotlib.cm as cm

mplColors = cm.datad.keys()

# Home page
@app.route("/")
def homePage():
    return searchPage("*",True)

@app.route("/about")
def aboutPage():
    return render_template("about.html")

@app.route("/upload-howto")
def uploadhowto():
    return render_template("upload-howto.html")

# Check file extention
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

# Store file in server
@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		zipfilename = str(request.files['filename'])
		tmpfilename = zipfilename.split('.')[0]
		if file and allowed_file(file.filename):
			try:
				if os.path.isdir(os.path.join(UPLOAD_FOLDER,tmpfilename)):
					shutil.rmtree(os.path.join(UPLOAD_FOLDER,tmpfilename))
				if os.path.exists(os.path.join(UPLOAD_FOLDER,zipfilename)):
					os.remove(os.path.join(UPLOAD_FOLDER,zipfilename))
			except OSError as e:
				print ("Error: %s - %s." % (e.filename, e.strerror))
			filename = secure_filename(file.filename)
			file.save(os.path.join(UPLOAD_FOLDER, filename))
			return('complete')
		else:
			return ('Error Uploading file, Try again')
	return render_template('upload.html')

@app.route('/fileparse', methods=['GET','POST'])
def fileparse():
	if request.method == 'POST':
		filename = request.form['filename']
		user = request.form['user']
		return(parse.parseData(filename,user))

@app.route('/downloadlog', methods=['POST'])
def downloadlog():
	from flask import send_file
	if request.method == 'POST':
		msgfile = request.form['filename']
		filelink = ('/pace/assets/static/logs/'+str(msgfile))
		try:
			return send_file(filelink,attachment_filename='message.log')
		except Exception as e:
			return str(e)

@app.route("/userauth", methods=['GET','POST'])
def userauth():
	if request.method == 'POST':
		username = request.form['user']
		searchuser = Authusers.query.filter_by(user=username).first()
		db.session.close()
		if searchuser is None:
			return ("invaliduser")
		else:
			return ("validuser")

@app.route('/login')
def login():

	# Generte and store a state in session before calling authorize_url
	if 'oauth_state' not in session:
		session['oauth_state'] = binascii.hexlify(os.urandom(24))

	# For unauthorized users, show link to sign in
	authorize_url = github.get_authorize_url(scope='', state=session['oauth_state'])
	return redirect(authorize_url)


@app.route('/callback')
def callback():
	#OAuth callback from GitHub
	code = request.args['code']
	state = request.args['state'].encode('utf-8')
	# Validate state param to prevent CSRF
	if state != session['oauth_state']:
		return render_template('error.html')

	# Request access token
	auth_session = github.get_auth_session(data={'code': code})
	session['access_token'] = auth_session.access_token

	# Call API to retrieve username.
	# `auth_session` is a wrapper object of requests with oauth access token
	r = auth_session.get('/user')
	session['username'] = r.json()['login']
	searchuser = Authusers.query.filter_by(user=session['username']).first()
	db.session.close()
	if searchuser is None:
		session['login']=False
		session.pop('username')
		session.pop('access_token')
		return render_template('notauth.html')
	else:
		session['login']=True
		try:
			redirectlink='/note/'+str(session['expid'])
		except KeyError:
			redirectlink='/'
		return redirect(redirectlink)

@app.route('/islogin')
def islogin():
	try:
		islogin=session['login']
		username = session['username']
		return (username)
	except:
		return ('')

@app.route('/logout')
def logout():
	try:
		# Delete session data
		session.pop('username')
		session.pop('access_token')
		session['login']=False
	except KeyError:
		return redirect('/')
	return redirect('/')

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


#A rest-like API that retrives a model-timing tree in JSON from the database
@app.route("/summaryQuery/<int:expID>/<rank>/",methods=["GET"])
def summaryQuery(expID,rank):
    resultNodes=""
    compset = "N/A"
    res="N/A"
    basePath = "/pace/"
    if os.getenv("PACE_DOCKER_INSTANCE") == "1":
        basePath+="portal/pace/"
    else:
        basePath+="assets/"
    basePath+="static/samples/"
    if expID == "-1":
        resultNodes = mt.parse(basePath+"model_timing.0000.new")
    elif expID == "-2":
        resultNodes = mt.parse(basePath+"model_timing_stats")
    else:
        resultNodes = db.engine.execute("select jsonVal from model_timing where expid = "+str(expID)+ " and rank = '"+rank+"'").fetchall()[0].jsonVal
        #Get user and machine information:
        tpData = db.engine.execute("select compset,res from e3smexp where expid = "+str(expID)).fetchall()
        compset,res = tpData[0].compset,tpData[0].res

    if rank == 'stats':
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
        resultNodes = json.dumps([newJson])
    return  '{{"obj":{0},"meta":{{"expid":"{1}","rank":"{2}","compset":"{3}","res":"{4}"}} }}'.format(resultNodes,expID,rank,compset,res)
@app.route("/exp-details/<int:mexpid>")
def expDetails(mexpid):
	myexp = None
	try:
		myexp = db.engine.execute("select * from e3smexp where expid= "+ str(mexpid) ).fetchall()[0]
	except IndexError:
		return render_template('error.html')
	mypelayout = db.engine.execute("select * from pelayout where expid= "+ str(mexpid) ).fetchall()
	myruntime = db.engine.execute("select * from runtime where expid= "+ str(mexpid) ).fetchall()
	ranks = db.engine.execute("select rank from model_timing where expid= "+ str(mexpid) ).fetchall()
	colorDict = {}
	for i in range(len(runtimeSvg.default_args['comps'])):
		colorDict[runtimeSvg.default_args['comps'][i]] = runtimeSvg.default_args['color'][i]
	try:
		noteexp = db.engine.execute("select * from expnotes where expid= "+ str(mexpid) ).fetchall()[0]
		note = noteexp.note
	except IndexError:
		note=""
	return render_template('exp-details.html', exp = myexp, pelayout = mypelayout, runtime = myruntime,expid = mexpid,ranks = ranks,chartColors = json.dumps(colorDict),note=note)

@app.route("/note/<expID>", methods=["GET","POST"])
def note(expID):
	session['expid']=expID
	try:
		userlogin = session['login']
	except KeyError:
		return redirect('/login')
	if userlogin == True:
		if request.method == "GET":
			try:
				myexpid = db.engine.execute("select * from e3smexp where expid= "+expID).fetchall()[0]
			except IndexError:
				return render_template('error.html')
			try:
				myexp = db.engine.execute("select * from expnotes where expid= "+expID).fetchall()[0]
				note = myexp.note
			except IndexError:
				note=""
			return render_template('note.html', note = note, expid = expID)
		elif request.method == "POST":
			note = request.form['note']		
			try:
				myexp = db.engine.execute("select * from expnotes where expid= "+expID).fetchall()[0]
				db.engine.execute("update expnotes set note =\'"+str(note)+"\' where expid = " +expID)
			except IndexError:
				db.engine.execute("insert into expnotes(expid,note) values ("+expID+",\'"+str(note)+"\')")
			return redirect('/exp-details/'+str(expID))
	else:
		return redirect('/login')

#Depcrecated version of the search page
"""@app.route("/exps")
def expsList():
    myexps = []
    # initDatabase()
    myexps = db.session.query(Timingprofile).order_by(Timingprofile.expid.desc()).limit(20)
    # myexps = Timingprofile.query.order_by(Timingprofile.expid.asc()).limit(25)
    return render_template('exps.html', explist = myexps)

EXPS_PER_RQ=20
@app.route("/ajax/exps/<int:pageNum>")
def expsAjax(pageNum):
    numexps = db.session.query(Timingprofile).count()
    myexps = db.session.query(Timingprofile).order_by(Timingprofile.expid.desc())[pageNum * EXPS_PER_RQ : (pageNum + 1) * EXPS_PER_RQ]
    pruned_data = {"numRows": numexps, "data": []}
    for exp in myexps:
	# var row = [o.expid,o.user,o.machine,o.total_pes_active,o.run_length,o.model_throughput,o.mpi_tasks_per_node,o.compset,o.grid];
        pruned_data["data"].append({"expid": exp.expid, "user": exp.user, "machine": exp.machine, "total_pes_active": exp.total_pes_active, "run_length": exp.run_length, "model_throughput": exp.model_throughput, "mpi_tasks_per_node": str(exp.mpi_tasks_per_node), "compset": exp.compset, "grid": exp.grid})
    return make_response(json.dumps(pruned_data))"""

#The search page! This is the primary navigation page for the site. It changes depending on where the user is on the site.
@app.route("/search/")
@app.route("/search/<searchQuery>")
def searchPage(searchQuery="*",isHomePage=False):
    homePageStr = False
    return render_template("search.html",sq = "var searchQuery = '"+searchQuery+"';",homePage = isHomePage)

#A redirect to /search/<searchQuery>/advsearch
#This is depricated, but here in case we have old urls:
@app.route("/advsearch/<searchQuery>")
def advSearch(searchQuery):
    return searchPage(searchQuery,False)

#This is a rest-like API that gives information about queried experiments from the e3smexp table.
@app.route("/ajax/search/<searchTerms>")
@app.route("/ajax/search/<searchTerms>/<limit>")
@app.route("/ajax/search/<searchTerms>/<limit>/")
@app.route("/ajax/search/<searchTerms>/<limit>/<orderBy>")
@app.route("/ajax/search/<searchTerms>/<limit>/<orderBy>/<ascDsc>")
def searchCore(searchTerms,limit = False,orderBy="expid",ascDsc="desc",whiteList = None,getRanks = True):
    resultItems = []
    filteredItems = []

    #Variable names are split into non-string and string respectively; this is to help improve search results during a basic search.
    variableList=[
        ["expid","total_pes_active","run_length","model_throughput","mpi_tasks_per_node","init_time","run_time"],
        ["user","machine","compset","exp_date","res","e3smexp.case"]
    ]

    specificVariables = whiteList
    if whiteList == None:
        specificVariables = variableList[0] + variableList[1]

    #This should be an easy way to determine if something's in the list
    if orderBy == "case":
        orderBy = "e3smexp.case"
    elif orderBy not in variableList[0] + variableList[1]:
        orderBy = "expid"
    #Only asc and desc are allowed:
    if ascDsc not in ["asc","desc"]:
        ascDsc = "desc"

    #Multiple queries can be used at one time; This helps separate them.
    querySet = set(searchTerms.replace(" ","+").split("|"))

    #If we have clashing "modes" (regular, advanced) in one query, we move those to its own query:
    queryDelete = [] #If we find clashing terms in one query, this is the list that deletes that index (that index is replaced by two differnet strings later)
    queryQue =  []
    for query in querySet:
        foundAdv = False
        foundBasic = False
        termTemp = query.replace(" ","+").split("+")

        #These strings hold terms in the query, just in case both advanced and basic syntax is present
        basicTemp = ""
        advTemp = ""
        for term in termTemp:
            if ":" in term:
                if foundAdv:
                    advTemp+="+"
                foundAdv = True
                advTemp+=term
            else:
                if foundBasic:
                    basicTemp+="+"
                foundBasic = True
                basicTemp+=term
        if foundAdv and foundBasic:
            queryQue.append(basicTemp)
            queryQue.append(advTemp)
            queryDelete.append(query)
    #Now to delete original queries:
    for index in queryDelete:
        querySet.discard(index)
    #Add in the new queries:
    for que in queryQue:
        querySet.add(que)

    #The original version of searchCore did not have these three functions separated... this is for cleaner code XP
    def searchAll(termString):
        queryStr = "select "+str(specificVariables).strip("[]").replace("'","")+" from e3smexp order by "+orderBy+" "+ascDsc
        if limit:
            queryStr+=" limit "+limit
        allResults = db.engine.execute(queryStr).fetchall()
        for result in allResults:
            resultItems.append(result)

    def advSearch(termString):
        termList = []
        #We assume the user is typing information with the following format: "user:name machine:titan etc:etc"
        for word in termString.split("+"):
            termList.append(word.replace(";","").replace("\\c",""))
        #Make a list of compiled variables to query in one swoop:
        strList = []
        for element in termList:
            syntax = element.split(":")
            #If the $ symbol is at the beginning, we go for an exact match, otherwise use 'like'
            elementStr = ""
            if syntax[1][0]=="$":
                elementStr = " = '"+syntax[1].strip("$")+"'"
            else:
                elementStr = ' like "%%'+syntax[1]+'%%"'

            if syntax[0] in variableList[0] + variableList[1]:
                strList.append(syntax[0]+elementStr)
            elif syntax[0] == "case":
                strList.append('e3smexp.case '+elementStr)
        compiledString = "select " + str(specificVariables).strip("[]").replace("'","") + " from e3smexp where "
        for i in range(len(strList)):
            compiledString+=strList[i]
            if not i==len(strList) - 1:
                compiledString+=" and "
        compiledString+=" order by "+orderBy+" "+ascDsc
        if limit:
            compiledString+=" limit "+limit+";"
        #Copy/paste from above:
        print(compiledString)
        allResults = db.engine.execute(compiledString).fetchall()
        for result in allResults:
            resultItems.append(result)

    def basicSearch(termString):
        termList = []
        #A regular search (no matchall)
        for word in termString.split("+"):
            termList.append(word.replace(";","").replace("\\c",""))
        #Remove empty strings: (spaces on the client side)
        while '' in termList:
            termList.remove('')
        #print(termList)

        if(len(termList) > 0):
            queryStr = "select " + str(specificVariables).strip("[]").replace("'","") + " from e3smexp where "
            for term in termList:
                #This controlls whether or not to search through number-based or string based variables:
                targetIndex = 0
                try:
                    decimal(term)
                except:
                    targetIndex+=1

                if not term == termList[0]:
                    queryStr+=" and "
                queryStr+='( '
                firstValue = True
                for word in variableList[targetIndex]:
                    if not firstValue:
                        queryStr+=" or "
                    #Equal an exact string if $ is at the beginning:
                    if term[0] == "$":
                        queryStr+=word+' = "'+term.strip("$")+'"'
                    else:
                        queryStr+=word+' like "%%'+term+'%%"'
                    firstValue = False
                queryStr +=" )"

            queryStr+=" order by "+orderBy+" "+ascDsc
            if limit:
                queryStr+=" limit "+limit
            print(queryStr)
            for result in db.engine.execute(queryStr).fetchall():
                resultItems.append(result)

    #All query types are defined,now to go through one query at a time...
    for element in querySet:
        if element == "*":
            searchAll(element)
        elif ":" in element:
            advSearch(element)
        else:
            basicSearch(element)

    #Once all queries are run, we filter out duplicates:
    for element in resultItems:
        unique = True
        for item in filteredItems:
            if str(element["expid"]) == str(item["expid"]):
                unique = False
                break
        if unique:
            resultDict = {}
            for key in element.keys():
                resultDict[key] = str(element[key])
            filteredItems.append(resultDict)

    #Grab the ranks based of of filteredItems:
    rankList = []
    if getRanks:
        for item in filteredItems:
            itemRanks = []
            queryResults = db.engine.execute("select rank from model_timing where expid = "+str(item["expid"])).fetchall()
            for result in queryResults:
                itemRanks.append(result.rank)
            rankList.append([itemRanks,[]])

    return json.dumps([filteredItems,rankList])

#Retrive specific values from /ajax/search. Order,asc/desc & limits are not a priority with this function:
@app.route("/ajax/specificSearch/<query>")
@app.route("/ajax/specificSearch/<query>/<whiteList>")
def specificSearch(query,whiteList = "total_pes_active,model_throughput,machine,run_time,expid"):
    whiteListArray = str(whiteList.replace("\\c","").replace(";","")).split(",")
    return json.dumps(json.loads(searchCore(query,False,"","",whiteListArray,False))[0])

@app.route("/searchSummary/")
@app.route("/searchSummary/<query>")
def searchSummary(query = ""):
    return render_template("searchSummary.html",query=query)

#Get a specific list of elements from e3smexp. Only specific elements are allowed, so users cannot grab everything.
@app.route("/ajax/getDistinct/<entry>")
def getDistinct(entry):
    queryList = []
    if entry in ["machine","user"]:
        distQuery = db.engine.execute("select distinct "+entry+" from e3smexp order by "+entry).fetchall()
        for element in distQuery:
            queryList.append(element[entry])
    return json.dumps(queryList)

#These three redirect to the search page with their respective category.
@app.route("/platforms/<platform>/")
def platformsRedirect(platform):
    return searchPage("machine:"+platform,False)

@app.route("/users/<user>/")
def usersRedirect(user):
    return searchPage("user:"+user,False)

@app.route("/benchmarks/<keyword>")
def benchmarksRedirect(keyword):
    splitStr = keyword.split(" ")
    return searchPage("compset:"+splitStr[0]+" res:"+splitStr[1],False)


#This is designed for the search bar on the website. It predicts what a user may be looking for based on where the dev specifies to search.
@app.route("/ajax/similarDistinct/<keyword>")
def searchPrediction(keyword):
    #The keyword is designed to be a single word without any potential database loopholes:
    keyword = keyword.replace("\\c","").replace(";","").replace(" ","")
    #Grab elements based on these columns:
    columnNames = ["user","machine","expid","compset","res","e3smexp.case"]
    resultWords = []
    for column in columnNames:
        colName = column
        if "." in column:
            colName = colName.split(".")[1]
        distQuery = db.engine.execute("select distinct "+column+" from e3smexp where "+column+" like '"+keyword+"%%' limit 10").fetchall()
        for element in distQuery:
            resultWords.append(str(element[colName]))
    #Sort them by similar name:
    # for i in range(len(resultWords)):
    #     if keyword[0] == resultWords[i][0]:
    #         for j in range(len(resultWords)):
    #             print(j)
    #             # or charCompare(resultWords[i],resultWords[j]
    #             if not keyword[0] == resultWords[j][0]:
    #                 temp = resultWords[j]
    #                 resultWords[j] = resultWords[i]
    #                 resultWords[i]=temp
    #                 break
    return json.dumps(resultWords)

#This generates an svg graph of runtime information. It makes use of an algorhythm created by donahue5 (modified to work with this project)
@app.route("/svg/runtime/<int:expid>")
def getRuntimeSvg(expid):
    resultElement = {}
    try:
        runtimeQuery = db.engine.execute("select * from runtime where expid = "+str(expid)).fetchall()
        for element in runtimeQuery:
            #These Decimal objects don't have "precision" values, while the ones in searchCore do... :/ [probably because of how these were queried]
            resultElement[element.component] = {"seconds":float(element.seconds),"model_years":float(element.model_years),"model_day":float(element.model_day)}
        for key in resultElement.keys():
            peQuery = db.engine.execute("select root_pe,tasks from pelayout where expid = "+str(expid)+" and component like '%%"+key+"%%'").fetchall()
            if len(peQuery) > 0:
                resultElement[key]["root_pe"] = peQuery[0].root_pe
                resultElement[key]["tasks"] = peQuery[0].tasks -1
        if len(resultElement.keys()) > 0:
            return Response(runtimeSvg.render(resultElement).read(),mimetype="image/svg+xml")
        else:
            return render_template('error.html'), 404
    except SQLAlchemyError:
        return render_template('error.html'), 404
