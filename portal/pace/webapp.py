#! /usr/bin/env python3

from flask import Flask,render_template,Response,make_response,send_from_directory,request,redirect,url_for, session
from collections import OrderedDict
from pace import app
#import parse as parse
from . import parse
import sys
import collections
import operator
import json
import urllib
from sqlalchemy.orm import sessionmaker
from . __init__ import db
import os, shutil, distutils
import re
import csv, io

#Model Timing Library:
from pace.e3sm.e3smParser import parseModelTiming
#modelTiming database information:
from . pace_common import *

from sqlalchemy.exc import SQLAlchemyError
#github imports
import binascii
from rauth import OAuth2Service
from . import tabulatorjson
# from . import xmljson2tabulator

GITHUB_CLIENT_ID, GITHUB_CLIENT_SECRET = getGithubkey()

github = OAuth2Service(
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    name='github',
    authorize_url='https://github.com/login/oauth/authorize',
    access_token_url='https://github.com/login/oauth/access_token',
    base_url='https://api.github.com/')


# ALLOWED_EXTENSIONS = set(['zip', 'tgz', 'gz', 'tar','txt'])
ALLOWED_EXTENSIONS = set(['zip'])
PACE_LOG_DIR,EXP_DIR,UPLOAD_FOLDER = getDirectories()

# Uploading file
from werkzeug.utils import secure_filename
import os
from pace.e3sm.e3smDb.datastructs import *

#These charts were modified for use on PACE
#Runtime image generator: by donahue5
#from . pe_layout_timings import pe_layout_timings as runtimeSvg
from pace import pe_layout_timings
#This is for querying colors:
from matplotlib.colors import to_rgb,to_hex
import matplotlib.cm as cm

mplColors = list(cm.datad.keys())

# Home page
@app.route("/")
def homePage():
    return searchPage("*",True)

@app.route("/about")
def aboutPage():
    numexps = db.engine.execute("select count(expid) from e3smexp ").first()[0]
    return render_template("about.html", nexps = numexps)

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
                print(("Error: %s - %s." % (e.filename, e.strerror)))
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
        project = request.form['project']
        if not bool(re.match('^[a-zA-Z0-9\-._]+$', user)):
            return('ERROR')
        # Check zip file names from pace-upload
        # Upon error, this path is being deleted, so we need to guard it
        # pace-exps-sarats-2021-02-04-003824.zip
        # pace-exps-user-timestamp.zip
        if not bool(re.match('^pace-exps-[a-zA-Z0-9\-_]+.zip$', filename)):
            return('ERROR')
        return(parse.parseData(filename,user,project))

@app.route('/downloadlog', methods=['POST'])
def downloadlog():
    from flask import send_file
    if request.method == 'POST':
        msgfile = request.form['filename']
        filelink = ('/pace/assets/static/logs/'+str(msgfile))
        try:
            if bool(re.match("^pace-[a-zA-Z0-9\-:]+\.log$", msgfile)):
                return send_file(filelink,attachment_filename='message.log')
            else :
                return render_template('error.html')
        except Exception as e:
            return str(e)

@app.route("/userauth", methods=['GET','POST'])
def userauth():
    if request.method == 'POST':
        username = request.form['user']
        if not bool(re.match('^[a-zA-Z0-9\-._]+$', username)):
            return ("invaliduser")
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
    try:
        if state != session['oauth_state']:
            return render_template('error.html')
    except:
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
        session.pop('login')
        session.pop('oauth_state')
        session.pop('expid')
    except KeyError:
        return redirect('/')
    return redirect('/')

# @app.route("/uploadlogin", methods=['GET','POST'])
# def uploadlogin():
#     if request.method == 'POST':
#         admin = request.form['name']
#         admin_pass = request.form['pass']
#         a=admin+admin_pass
#         z=int(len(a))
#         b=''
#         for i in range(z):
#             b = b + chr(ord(a[i]) + 2)
#         c=b+a
#         y=int(len(c))
#         d=''
#         for i in range(y):
#             d = d + chr(ord(c[i])+1)
#         f=open('/pace/dev1/portal/pace/pass.txt','r')
#         for line in f:
#             admin = line.split(None,1)[0]
#             print(admin)
#             if admin==d:
#                 return("ok")
#
#         return("not")

# Error handler
@app.errorhandler(404)
def page_not_found(error):
    return render_template('error.html'), 404

@app.route("/searchTips/")
def searchTips():
    return render_template("searchTips.html")

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
@app.route("/summaryQuery/<int:expID>/<rank>/<getFullStats>",methods=["GET"])
def summaryQuery(expID,rank,getFullStats = ""):
    # Rank can be a number or stats referring to global statistics file
    if not bool(re.match('(^stats$)|(^[0-9]+$)', rank)):
        return render_template('error.html')
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
        resultNodes = parseModelTiming.parse(basePath+"model_timing.0000.new")
    elif expID == "-2":
        resultNodes = parseModelTiming.parse(basePath+"model_timing_stats")
    else:
        resultNodes = db.engine.execute("select jsonVal from model_timing where expid = "+str(expID)+ " and rank = '"+rank+"'").fetchall()[0].jsonVal
        #Get user and machine information:
        tpData = db.engine.execute("select compset,res from e3smexp where expid = "+str(expID)).fetchall()
        compset,res = tpData[0].compset,tpData[0].res

    if rank == 'stats' and not getFullStats == "getFullStats":
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

@app.route("/flamegraph/<expid>/<rank>/")
def flameGraph(expid,rank):
    if bool(re.match('^[0-9,]+$', rank)) and bool(re.match('^[0-9,]+$', expid)):
      return render_template("flameGraph.html",expid=expid,rank=rank.split(','))

@app.route("/scorpio/<int:mexpid>")
def scorpioIOStat(mexpid):
    #get data
    try:
        if not isinstance(mexpid,int):
            return render_template('error.html')
        scorpio_data = db.engine.execute("select data from scorpio_stats where name = 'spio_stats' and expid="+str(mexpid)).first()
        scorpio_json_data = json.loads(scorpio_data[0])
        
        myexp = db.engine.execute("select * from e3smexp where expid= "+ str(mexpid) ).fetchall()[0]
        modelRuntime = myexp.run_time

        overalData = scorpio_json_data["ScorpioIOSummaryStatistics"]["OverallIOStatistics"]
        
        modelData = scorpio_json_data["ScorpioIOSummaryStatistics"]["ModelComponentIOStatistics"]

        fileIOData = scorpio_json_data["ScorpioIOSummaryStatistics"]["FileIOStatistics"]

        readIOData = []
        writeIOData = []

        for fdata in fileIOData:
            if fdata['tot_rtime(s)']!=0:
                readIOData.append(fdata)
            if fdata['tot_wtime(s)']!=0:
                writeIOData.append(fdata)

    except Exception as e:
        print('Error:')
        print(e)
        return render_template('error.html')
    return render_template('scorpioIOpage.html', overalData = overalData, modelData = modelData,
                            readIOData=readIOData,writeIOData=writeIOData, modelRuntime = modelRuntime)

@app.route("/buildtime/<int:mexpid>")
def buildtime(mexpid):
    try:
        if not isinstance(mexpid,int):
            return render_template('error.html')
        data = db.engine.execute("select data from build_time where expid="+str(mexpid)).first()
        jsonData = json.loads(data[0])
        if not jsonData or ('data' in jsonData and jsonData['data'] == 'None'):
            return render_template('customMessagepage.html', message = 'Data not available for this experiment')
        
        tabledata = []
        for node in jsonData:
            model={
                'name':None,
                'time':None
            }
            model['name']=node
            model['time']=jsonData[node]
            tabledata.append(model)
    except Exception as e:
        print('Error:')
        print(e)
        return render_template('error.html')
    return render_template('buildtime.html', test = jsonData, tabledata = tabledata)

@app.route("/memoryprofile/<int:mexpid>")
def memoryProfileStat(mexpid):
    try:
        if not isinstance(mexpid,int):
            return render_template('error.html')
        
        TOD = []
        VSZ = {}
        RSS = {}

        memory_profile_data = db.engine.execute("select data from memfile_inputs where name = 'memory' and expid="+str(mexpid)).first()
        memory_csv_data = memory_profile_data[0]
        reader = csv.DictReader(io.StringIO(memory_csv_data))
        jsonData = json.dumps(list(reader))
        jsonData = json.loads(jsonData)
        
        for node in jsonData:
            for key in node:
                if key == '#TOD':
                    TOD.append(float(node[key]))
                elif key.startswith(' RSS'):
                    if key.strip() not in RSS:
                        RSS[key.strip()] = [float(node[key].strip())]
                    else:
                        RSS[key.strip()].append(float(node[key].strip()))
                elif key.startswith(' VSZ'):
                    if key.strip() not in VSZ:
                        VSZ[key.strip()] = [float(node[key].strip())]
                    else:
                        VSZ[key.strip()].append(float(node[key].strip()))
        if not TOD:
            return render_template('customMessagepage.html',message = "Memory Data not available for this experiment")
    except Exception as e:
        print('Error:')
        print(e)
        return render_template('error.html')
    return render_template('memoryProfilePage.html',TOD = TOD, RSS = RSS, VSZ = VSZ)

@app.route("/exp-details/<int:mexpid>")
def expDetails(mexpid):
    myexp = None
    myxmls = None
    mynmls = None
    myrcs = None
    try:
        myexp = db.engine.execute("select * from e3smexp where expid= "+ str(mexpid) ).fetchall()[0]
        myxmls = db.engine.execute("select name from xml_inputs where expid= "+ str(mexpid) ).fetchall()
        mynmls = db.engine.execute("select name from namelist_inputs where expid= "+ str(mexpid) ).fetchall()
        myrcs = db.engine.execute("select name from rc_inputs where expid= "+ str(mexpid) ).fetchall()
    except IndexError:
        return render_template('error.html')
    mypelayout = db.engine.execute("select * from pelayout where expid= "+ str(mexpid) ).fetchall()
    myruntime = db.engine.execute("select * from runtime where expid= "+ str(mexpid) ).fetchall()
    ranks = db.engine.execute("select rank from model_timing where rank!= 'stats' and expid= "+ str(mexpid) + " order by cast(rank as int)" ).fetchall()
    colorDict = {}
    for i in range(len(pe_layout_timings.default_args['comps'])):
        colorDict[pe_layout_timings.default_args['comps'][i]] = pe_layout_timings.default_args['color'][i]
    try:
        noteexp = db.engine.execute("select * from expnotes where expid= "+ str(mexpid) ).fetchall()[0]
        note = noteexp.note
    except IndexError:
        note=""
    
    
    scorpioStatsId = False
    memoryProfileId = False
    buildTimeId = False
    try:
        #check if we have scorpio data
        scorpioData = db.engine.execute("select name from scorpio_stats where expid="+str(mexpid)).fetchone()
        if not scorpioData:
            scorpioStatsId = False
        else:
            scorpioStatsId = True
        
        # check if we have build time data
        buildFileData = db.engine.execute("select data from build_time where expid="+str(mexpid)).first()
        if not buildFileData:
            buildTimeId = False
        else:
            buildTimeId = True
        
        #check if we have memory data
        memData = db.engine.execute("select data from memfile_inputs where name = 'memory' and expid="+str(mexpid)).first()
        if not memData:
            memoryProfileId = False
        else:
            memoryProfileId = True
    except Exception as e:
        print(e)
        return render_template('error.html')

    runtimes=[]
    for runs in myruntime:
        run = {
            'component':runs[2],
            'seconds':float(runs[3]),
            'model_day':float(runs[4]),
            'model_years':float(runs[5])
        }
        runtimes.append(run)
    return render_template('exp-details.html', runtimes = runtimes,exp = myexp, pelayout = mypelayout, runtime = myruntime,expid = mexpid, \
            ranks = ranks,chartColors = json.dumps(colorDict),note=note, \
            xmls = myxmls, nmls = mynmls, rcs = myrcs, \
            scorpioStatsId = scorpioStatsId, memoryProfileId = memoryProfileId, buildTimeId = buildTimeId \
            )

@app.route("/exp-details-old/<int:mexpid>")
def expDetailsOld(mexpid):
    myexp = None
    myxmls = None
    mynmls = None
    myrcs = None
    try:
        myexp = db.engine.execute("select * from e3smexp where expid= "+ str(mexpid) ).fetchall()[0]
        myxmls = db.engine.execute("select name from xml_inputs where expid= "+ str(mexpid) ).fetchall()
        mynmls = db.engine.execute("select name from namelist_inputs where expid= "+ str(mexpid) ).fetchall()
        myrcs = db.engine.execute("select name from rc_inputs where expid= "+ str(mexpid) ).fetchall()
    except IndexError:
        return render_template('error.html')
    mypelayout = db.engine.execute("select * from pelayout where expid= "+ str(mexpid) ).fetchall()
    myruntime = db.engine.execute("select * from runtime where expid= "+ str(mexpid) ).fetchall()
    ranks = db.engine.execute("select rank from model_timing where rank!= 'stats' and expid= "+ str(mexpid) + " order by cast(rank as int)" ).fetchall()
    colorDict = {}
    for i in range(len(pe_layout_timings.default_args['comps'])):
        colorDict[pe_layout_timings.default_args['comps'][i]] = pe_layout_timings.default_args['color'][i]
    try:
        noteexp = db.engine.execute("select * from expnotes where expid= "+ str(mexpid) ).fetchall()[0]
        note = noteexp.note
    except IndexError:
        note=""
    return render_template('exp-details-old.html', exp = myexp, pelayout = mypelayout, runtime = myruntime,expid = mexpid, \
            ranks = ranks,chartColors = json.dumps(colorDict),note=note, \
            xmls = myxmls, nmls = mynmls, rcs = myrcs \
            )

@app.route("/useralias/<user>")
def useralias(user):
    if bool(re.match('^[a-zA-Z0-9\-._]+$', user)):
        try:
            validuser=db.engine.execute("select * from authusers where user='"+str(user)+"\'").fetchall()[0]
        except IndexError:
            return render_template('error.html')
        try:
            alias=db.engine.execute("select alias from useralias where user='"+str(user)+"\'").fetchall()
        except IndexError:
            alias=""
        return render_template('useralias.html',alias = alias, user = user)
    else:
        return render_template('error.html')

@app.route("/useraliasdelete", methods=['POST'])
def useraliasdelete():
    if request.method=='POST':
        user = request.form['user']
        alias = request.form['delete']
        if not bool(re.match('^[a-zA-Z0-9\-_.]+$', user)):
            return render_template('error.html')
        if not bool(re.match('^[a-zA-Z0-9\-_.]+$', alias)):
            return render_template('error.html')
        try:
            db.engine.execute("delete from useralias where alias='"+alias+"\'")
        except:
            return render_template('error.html')
        return redirect('/useralias/'+str(user))
    if request.method=='GET':
        return render_template('error.html')
@app.route("/useraliasadd", methods=['POST','GET'])
def useraliasadd():
    if request.method=='POST':
        user = request.form['user']
        alias = request.form['alias']
        if not bool(re.match('^[a-zA-Z0-9\-_.]+$', user)):
            return render_template('error.html')
        if not bool(re.match('^[a-zA-Z0-9\-_.]+$', alias)):
            return render_template('error.html')
        try:
            db.engine.execute("insert into useralias(user,alias) values ('"+user+"\',\'"+alias+"\')")
        except:
            return render_template('error.html')
        return redirect('/useralias/'+str(user))
    if request.method=='GET':
        return render_template('error.html')
@app.route("/note/<int:expID>", methods=["GET","POST"])
def note(expID):
    session['expid']=expID
    try:
        userlogin = session['login']
    except KeyError:
        return redirect('/login')
    if userlogin == True:
        if request.method == "GET":
            try:
                myexpid = db.engine.execute("select * from e3smexp where expid= "+str(expID)).fetchall()[0]
            except IndexError:
                return render_template('error.html')
            try:
                myexp = db.engine.execute("select * from expnotes where expid= "+ str(expID)).fetchall()[0]
                note = myexp.note
            except IndexError:
                note=""
            return render_template('note.html', note = note, expid = expID)
        elif request.method == "POST":
            note = request.form['note']
            try:
                myexp = db.engine.execute("select * from expnotes where expid= "+ str(expID)).fetchall()[0]
                db.engine.execute("update expnotes set note =\'"+str(note)+"\' where expid = " + str(expID))
            except IndexError:
                db.engine.execute("insert into expnotes(expid,note) values ("+ str(expID) +",\'"+str(note)+"\')")
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
    if bool(re.match('^[\sa-zA-Z0-9\-_\.,\*:$|]+$', searchQuery)):
        return render_template("search.html",sq = "var searchQuery = '"+searchQuery+"';",homePage = isHomePage)
    else:
        return render_template('error.html')

#A redirect to /search/<searchQuery>/advsearch
#This is depricated, but here in case we have old urls:
@app.route("/advsearch/<searchQuery>")
def advSearch(searchQuery):
    return searchPage(searchQuery,False)

#This is a rest-like API that gives information about queried experiments from the e3smexp table.
@app.route("/ajax/search/<searchTerms>")
@app.route("/ajax/search/<searchTerms>/<int:mlimit>")
@app.route("/ajax/search/<searchTerms>/<int:mlimit>/")
@app.route("/ajax/search/<searchTerms>/<int:mlimit>/<orderBy>")
@app.route("/ajax/search/<searchTerms>/<int:mlimit>/<orderBy>/<ascDsc>")
# Think if you want to specify default limit
# Sarat: Note that limit is expecting a string here
def searchCore(searchTerms,mlimit = 50,orderBy="exp_date",ascDsc="desc",whiteList = None,getRanks = True):
    resultItems = []
    filteredItems = []

    # Convert user-passed to string after it passes integer validation
    limit = str(mlimit)
    # Double-check that limit is a valid number
    if not bool(re.match('^[0-9]+$', limit)):
        return render_template('error.html')

    # Search terms should not contain any special characters except - _ * . , : + ($ under evaluation, | presently allowed)
    # Since some special characters should be escaped with a \ even within regular expression character set,
    # we have escaped every special character below to be safe
    # + needs to be allowed as search bar on website formulates queries using that as delimiter
    # * definitely needs to be allowed as it is used for home page
    # Disallowed: `~@#$%^&()={}[]\\|\'";:<>?/
    if bool(re.search('[\`\~\@\#\$\%\^\&\(\)\=\{\}\[\]\\\'\"\;\<\>\?\/]', searchTerms)):
        return render_template('error.html')

    # Allowed chars in search terms
    # * is an acceptable search term especially for getting home page results
    # \s is the whitespace character
    if not bool(re.match('^[\sa-zA-Z0-9\-_\.,\*:$\|+]+$', searchTerms)):
        return render_template('error.html')

    # TODO: Mitigate boolean OR
    # if searchTerms.__contains__("OR") or searchTerms.__contains__("or"):
        # return render_template('error.html')

    #Variable names are split into non-string and string respectively. This is because mysql doesn't like comparing strings with numbers. It should therfore be able to fix exact matches, as there is only a string-to-string comparison
    variableList=[
        ["expid","total_pes_active","run_length","model_throughput","mpi_tasks_per_node","init_time","run_time"],
        ["user","machine","compset","exp_date","res","e3smexp.case","lid"]
    ]

    # Sarat (Feb 3,2021): orderby handling is a security issue. There could be
    # malicious content after valid fields, so truncate
    # "exp_date)) AS LwZg WHERE 8064=8064;SELECT SLEEP(5)#"
    # Note: you need not allow . here as e3smexp.case will be added latter when needed
    if not bool(re.match('^[a-zA-Z_]+$', orderBy)):
        return render_template('error.html')
    if not bool(re.match('^(a|(de))sc$', ascDsc)):
        return render_template('error.html')

    # case is a reserved word in mySQL, so use table name
    if orderBy == "case":
        orderBy = "e3smexp.case"
    elif orderBy not in variableList[0] + variableList[1]:
        orderBy = "expid"
    #Only asc and desc are allowed:
    if ascDsc not in ["asc","desc"]:
        ascDsc = "desc"

    #  whiteList is an array
    # if whiteList != None:
        # if not bool(re.match('^[\sa-zA-Z0-9\-_\.\*$:|,]+$', whiteList)):
            # return render_template('error.html')
    if whiteList == None:
        specificVariables = variableList[0] + variableList[1]
    else:
        # TODO: Check whitelist vars when whiteList is not none
        for wvar in whiteList:
            if not bool(re.match('^[a-zA-Z_\.]+$', wvar)):
                return render_template('error.html')
        specificVariables = whiteList    

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
        if not bool(re.match('^[\sa-zA-Z0-9\-_\.,\*:$|+]+$', termString)):
            return render_template('error.html')
        queryStr = "select "+str(specificVariables).strip("[]").replace("'","")+" from e3smexp order by "+orderBy+" "+ascDsc
        if limit:
            queryStr+=" limit "+ str(limit)
        allResults = db.engine.execute(queryStr).fetchall()
        for result in allResults:
            resultItems.append(result)

    def advSearch(termString):
        if not bool(re.match('^[\sa-zA-Z0-9\-_\.,\*:$|+]+$', termString)):
            return render_template('error.html')
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
        if not bool(re.match('^[\sa-zA-Z0-9\-_\.,\*:$|+]+$', termString)):
            return render_template('error.html')
        termList = []
        #A regular search (no matchall)
        for word in termString.split("+"):
            termList.append(word.replace(";","").replace("\\c",""))
        #Remove empty strings: (spaces on the client side)
        while '' in termList:
            termList.remove('')
        

        if(len(termList) > 0):
            queryStr = "select " + str(specificVariables).strip("[]").replace("'","") + " from e3smexp where "
            for term in termList:
                #This controlls whether or not to search through number-based or string based variables:
                targetIndex = 0
                try:
                    float(term.strip("$"))
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
            for key in list(element.keys()):
                resultDict[key] = str(element[key])
            filteredItems.append(resultDict)

    #Grab the ranks based of of filteredItems:
    rankList = []
    if getRanks:
        for item in filteredItems:
            itemRanks = []
            queryResults = db.engine.execute("select rank from model_timing where expid = " + str(item["expid"]) + " order by cast(rank as int)" ).fetchall()
            for result in queryResults:
                itemRanks.append(result.rank)
            rankList.append([itemRanks,[]])

    return json.dumps([filteredItems,rankList])

# Sarat (Feb 3, 2021): This function is used by the scatter plot and sends
# requests of the form https://pace.ornl.gov/ajax/specificSearch/*/expid,machine,model_throughput,total_pes_active
#Retrive specific values from /ajax/search. Order,asc/desc & limits are not a priority with this function:
@app.route("/ajax/specificSearch/<query>")
@app.route("/ajax/specificSearch/<query>/<whitelist>")
def specificSearch(query,whitelist = "total_pes_active,model_throughput,machine,run_time,expid"):
    # We need to allow comma  , here to allow scatter plot to work
    if not bool(re.match('^[\sa-zA-Z0-9\-_.*$:| +,]+$', query)):
      return render_template('error.html')
    if whitelist != None:
        # Whitelist would need alphanumeric chars and , and probably + for delimiting
        if not bool(re.match('^[\sa-zA-Z_+,]+$', whitelist)):
            return render_template('error.html')
        whiteListArray = str(whitelist.replace("\\c","").replace(";","")).split(",")
    # Scatter plot uses this interface to request data for plotting, specify default limit of 50
    # Note: limit is expecting a string value
    try:
        # Check if valid json, Error page returned if search contains forbidden chars
        result = json.loads(searchCore(query,50,"exp_date","desc",whiteListArray,False))
        retval = json.dumps(result[0])
        return retval
    except ValueError as e:
         return ('ERROR')

#@app.route("/searchSummary/")
#@app.route("/searchSummary/<query>")
#def searchSummary(query = ""):
#    if not bool(re.match('^[\sa-zA-Z0-9\-_.*$:| +]+$', query)):
#      return render_template('error.html')
#    return render_template("searchSummary.html",query=query)

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
    if bool(re.match('^[a-zA-Z0-9\-_]+$', platform)):
        return searchPage("machine:"+platform,False)
    else:
        return render_template('error.html')

@app.route("/users/<user>/")
def usersRedirect(user):
    if bool(re.match('^[a-zA-Z0-9\-_]+$', user)):
        return searchPage("user:"+user,False)
    else:
        return render_template('error.html')

@app.route("/benchmarks/<keyword>")
def benchmarksRedirect(keyword):
    if not bool(re.match('^[\sa-zA-Z0-9\-\._:]+$', keyword)):
        return render_template('error.html')
    splitStr = keyword.split(" ")
    if splitStr[0] in ["FC5AV1C-H01A", "GMPAS-IAF"]:
      return searchPage("compset:"+splitStr[0]+" res:"+splitStr[1],False)
    else:
      return render_template('error.html')

#This is designed for the search bar on the website. It predicts what a user may be looking for based on where the dev specifies to search.
@app.route("/ajax/similarDistinct/<keyword>")
def searchPrediction(keyword):
    if not bool(re.match('^[a-zA-Z0-9\-._]+$', keyword)):
        return render_template('error.html')
    #The keyword is designed to be a single word without any potential database loopholes:
    keyword = keyword.replace("\\c","").replace(";","").replace(" ","")
    #Grab elements based on these columns:
    columnNames = ["user","machine","expid","compset","res","e3smexp.case","lid"]
    resultWords = []
    for column in columnNames:
        colName = column
        if "." in column:
            colName = colName.split(".")[1]
        distQuery = db.engine.execute("select distinct "+column+" from e3smexp where "+column+" like '"+keyword+"%%' limit 10").fetchall()
        for element in distQuery:
            if not element[colName] in resultWords:
                resultWords.append(str(element[colName]))
    #Sort them by similar name:
    # keywordReg = re.compile(keyword)
    # for i in range(len(resultWords)):
    #     if keywordReg.search(resultWords[i][0]):
    #         for j in range(len(resultWords)):
    #             print(j)
    #             # or charCompare(resultWords[i],resultWords[j]
    #             if not keywordReg.search(resultWords[j][0]):
    #                 temp = resultWords[j]
    #                 resultWords[j] = resultWords[i]
    #                 resultWords[i]=temp
    #                 break
    return json.dumps(resultWords)

#This generates an svg graph of runtime information. It is adapted from Donahue's script.
@app.route("/svg/runtime/<int:expid>")
def getRuntimeSvg(expid):
    resultElement = {}
    try:
        runtimeQuery = db.engine.execute("select * from runtime where expid = "+str(expid)).fetchall()
        for element in runtimeQuery:
            #These Decimal objects don't have "precision" values, while the ones in searchCore do... :/ [probably because of how these were queried]
            resultElement[element.component] = {"seconds":float(element.seconds),"model_years":float(element.model_years),"model_day":float(element.model_day)}
        for key in list(resultElement.keys()):
            peQuery = db.engine.execute("select root_pe,tasks from pelayout where expid = "+str(expid)+" and component like '%%"+key+"%%'").fetchall()
            if len(peQuery) > 0:
                resultElement[key]["root_pe"] = peQuery[0].root_pe
                resultElement[key]["tasks"] = peQuery[0].tasks -1
        if len(list(resultElement.keys())) > 0:
            return Response(pe_layout_timings.render(resultElement).read(),mimetype="image/svg+xml")
        else:
            return render_template('error.html'), 404
    except SQLAlchemyError:
        return render_template('error.html'), 404

@app.route("/atmos/<expids>/")
def atmosChart(expids):
    if not bool(re.match('^[0-9,]+$', expids)):
        return render_template('error.html')
    atm_timer = [
        "a:moist_convection",
        "a:macrop_tend",
        "a:tphysbc_aerosols",
        "a:microp_aero_run",
        "a:microp_tend",
        "a:radiation",
        "a:phys_run2",
        "a:stepon_run3",
        "a:stepon_run1",
        "a:stepon_run2",
        "a:wshist",
        "CPL:ATM_RUN"
    ]
    sampleModel = {
        'children': [],
        'multiParent': False,
        'name': '',
        'values':{
            'count': 0,
            'on': False,
            'processes': 0,
            'threads': 0,
            'wallmax': 0,
            'wallmax_proc': 0,
            'wallmax_thrd': 0,
            'wallmin': 0,
            'wallmin_proc': 0,
            'wallmin_thrd': 0,
            'walltotal': 0
        }
    }
    expidlist = expids.split(',')
    for id in expidlist:
        try:
            expid = int(id)
        except:
            return render_template('error.html')
    try:
        # single experiment detail page
        if len(expidlist)==1:
            resultNodes = db.engine.execute("select jsonVal from model_timing where expid = %s and rank = 'stats'",(expidlist[0],)).fetchall()[0].jsonVal
            data = json.loads(resultNodes)
            
            result = {}
            for model in data[0]:
                if model['name'] in atm_timer:
                    result[model['name']] = model
                elif model['name'] == "a:bc_aerosols":
                    result['a:tphysbc_aerosols'] = model   
            
            for name in atm_timer:
                if name not in result:
                    sampleModel['name'] = name
                    result[name] = sampleModel
            return render_template("atmos.html",expids = expidlist[0], rd = result)
        # compare atm page
        else:
            output = {}
            for expid in expidlist:
                resultNodes = db.engine.execute("select jsonVal from model_timing where expid = %s and rank = 'stats'",(expid,)).fetchall()[0].jsonVal
                data = json.loads(resultNodes)
                result = {}
                for model in data[0]:
                    if model['name'] in atm_timer:
                        result[model['name']] = model
                    elif model['name'] == "a:bc_aerosols":
                        result['a:tphysbc_aerosols'] = model 
                
                for name in atm_timer:
                    if name not in result:
                        sampleModel['name'] = name
                        result[name] = sampleModel
                output[expid] = result
            return render_template('atmosCompare.html', expids = expidlist, rd = output)
    except:
        return render_template('error.html')
    


@app.route("/xmlviewer/<int:mexpid>/<mname>")
def xmlViewer(mexpid, mname):
    if not bool(re.match('^[a-zA-Z0-9\-_.]+$', mname)):
        return render_template('error.html')
    data = db.engine.execute("select data from xml_inputs where expid=" + str(mexpid) + " and name='" + mname + "';" ).first()
    if data is None:
        return render_template('error.html')
    # tabledata = xmljson2tabulator.xmljson2tabulator(data[0])
    # return render_template("tabulator.html", myjson = tabledata)
    return render_template("json.html", myjson = data[0])

@app.route("/nmlviewer/<int:mexpid>/<mname>")
def nmlViewer(mexpid, mname):
    if not bool(re.match('^[a-zA-Z0-9\-_.]+$', mname)):
        return render_template('error.html')
    data = db.engine.execute("select data from namelist_inputs where expid=" + str(mexpid) + " and name='" + mname + "';" ).first()
    if data is None:
        return render_template('error.html')
    tabledata = tabulatorjson.nestedjson2tabulator(data[0])
    return render_template("tabulator.html", myjson = tabledata)
    # return render_template("json.html", myjson = tabledata)

@app.route("/rcviewer/<int:mexpid>/<mname>")
def rcViewer(mexpid, mname):
    if not bool(re.match('^[a-zA-Z0-9\-_.]+$', mname)):
        return render_template('error.html')
    data = db.engine.execute("select data from rc_inputs where expid=" + str(mexpid) + " and name='" + mname + "';" ).first()
    if data is None:
        return render_template('error.html')
    # tabledata = tabulatorjson.nestedjson2tabulator(data[0])
    # return render_template("tabulator.html", myjson = tabledata)
    return render_template("json.html", myjson = data[0])
