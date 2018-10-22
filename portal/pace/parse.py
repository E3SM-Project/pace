#from data import db
#from data import ModelTiming, Timingprofile, Pelayout, Runtime
from datastructs import *
from pace_common import *
db.create_all()
import array
import sys,os
import gzip
import tarfile
import shutil
import zipfile
import pymysql
import types

import modelTiming as mt
import io

def parseData():
	# start main
	# upload directory
	tmp_updir='/pace/prod/portal/upload/'
	old_stdout = sys.stdout
	log_file = open('message.log','w')
	sys.stdout = log_file
	try:	
		fpath=tmp_updir
		# Extract aggregated zip files
		zip_ref=zipfile.ZipFile(tmp_updir+'experiments.zip','r')
		zip_ref.extractall(fpath)
		zip_ref.close
	
		# list and store path of all new uploaded file
		dic=[]
		for i in os.listdir(fpath):
			dic.append(os.path.join(fpath,i))


		# untar, if tar file exists
		for i in range(len(dic)):
			if dic[i].endswith('.tar.gz'):
				tar = tarfile.open(dic[i])
				tar.extractall()
				tar.close()

		# store path of all directorie
		dic1=[]
		for i in os.listdir(fpath):
			if i !='parse.py' and i!='upload' and i!='experiments.zip':	
				dic1.append(i)


		# "e3sm_timing." file list		
		allfile=[]
		# "timing." file list
		timingfile=[]
		# "README.case." file list
		readmefile=[]
		# "GIT_DESCRIBE." file list
		gitdescribefile=[]
		# go through all directories and grab certain files for parsing		
		for i in range(len(dic1)):
			root=os.path.join(fpath,dic1[i])
			for path, subdirs, files in os.walk(root):
				for name in files:
					if name.startswith("timing."):
						timingfile.append(os.path.join(path, name))
					if name.startswith("e3sm_timing."):		
						allfile.append(os.path.join(path, name))
					if name.startswith("README.case."):
						readmefile.append(os.path.join(path, name))
					if name.startswith("GIT_DESCRIBE."):
						gitdescribefile.append(os.path.join(path, name))
	except IOError as e:
		return('Error: %s' % e.strerror)
	except OSError as e:
		return('Error: %s' % e.strerror)
	
	# parse and store timing profile file in a database
	for i in range(len(allfile)):
		# insert experiments for given files
		isSuccess=insertExperiment(allfile[i],readmefile[i],timingfile[i],gitdescribefile[i],db,fpath)
		
	
	# remove uploaded experiments
	removeFolder(tmp_updir)
	sys.stdout = old_stdout
	log_file.close()
	if isSuccess == True:
		return('success')
	else:
		return('Error: Check message.log')

# 
def spaceConcat(phraseIn,subGroup = False,filter="\n\t"):
    phraseIn = phraseIn.strip(filter)
    #Destroy spaces by default:
    phraseSplit = phraseIn.split(" ")
    total=[""]
    currPhrase = 0
    onWord = False
    firstPhrase = True
    for i in range(len(phraseSplit)):
        if onWord or not phraseSplit[i] == "":
            if not onWord:
                onWord = True
                if not subGroup or not firstPhrase:
                    total.append("")
            firstPhrase = False
            addWord = True
            #Ignore newlines:
            if phraseSplit[i]  == "":
                onWord = False
                addWord = False
                if subGroup:
                    currPhrase+=1
            if addWord:
                if not len(total[currPhrase]) == 0:
                    total[currPhrase]+=" "
                total[currPhrase]+=phraseSplit[i]
    return total
#Returns a list of items from the table. This is different because of how the data itself is structured. If "component" makes a good way to address these values, I'm open to making this return a dictionary.
def tableParse(lineInput):
    names=["component","comp_pes","root_pe","tasks","threads","instances","stride"]
    resultList=[]
    for item in lineInput:
        splitValues = spaceConcat(item,True)
        tableColumn={}
        for i in range(len(names)):
            tableColumn[names[i]] = splitValues[i].strip("(")
        resultList.append(tableColumn)
    return resultList

def changeDateTime(c_date):
	from time import strptime
	from datetime import datetime
	thatdate = c_date.split()
	hhmmss=thatdate[3]
	mm=strptime(thatdate[1],'%b').tm_mon
	yy=thatdate[4].rstrip('\n')
	dd=thatdate[2]
	dtime=yy+'-'+str(mm)+'-'+dd+' '+hhmmss
	return(dtime)

def checkDuplicateExp(ecase,elid,euser):
	flag=Timingprofile.query.filter_by(case=ecase,lid=elid,user=euser).first()
	if flag is None:
		return(False)
	else:
		return(True)

def parseReadme(fileIn):
	resultElement = {}
	commandLine = None
	flag=False
	for commandLine in fileIn:
		word=commandLine.split(" ")
		for element in word:
			if ('create_newcase' in element):
				cmdArgs = commandLine.split(": ",1)[1].strip("./\n").split(" ")
				resultElement["name"] = cmdArgs[0]
				for i in range(len(cmdArgs)):
					if cmdArgs[i][0] == "-":
						if "=" in cmdArgs[i]:
							argumentStr = cmdArgs[i].strip("-").split("=")
							resultElement[argumentStr[0]] = argumentStr[1]
						else:
							argument = cmdArgs[i].strip("-")
							resultElement[argument] = cmdArgs[i+1]
					resultElement["date"] = commandLine.split(": ",1)[0].strip(":")
				break
		if 'res' in resultElement.keys():		
			break	
	return resultElement

def parseModelVersion(gitfile):
	if gitfile.endswith('.gz'):
		parsefile = gzip.open(gitfile,'rb')
	else:
		parsefile = open(gitfile, 'rb')
	version = 0
	for line in parsefile:
		version = line.strip('\n')
		break
	parsefile.close()
	return version

def insertExperiment(filename,readmefile,timingfile,gitfile,db,fpath):
	if filename.endswith('.gz'):
		parseFile=gzip.open(filename,'rb')
	else:
		parseFile=open(filename,'rb')	
	timingProfileInfo={}
	componentTable=[]
	runTimeTable=[]
	duplicateFlag=False
	word=''
	for line in parseFile:
		if line!='\n':
			if len(timingProfileInfo)<12:		
				word=line.split(None,3)
				if word[0]=='Case':
					timingProfileInfo['case']=word[2]
				elif word[0]=='LID':
					timingProfileInfo['lid']=word[2]
				elif word[0]=='Machine':
					timingProfileInfo['machine']=word[2]
				elif word[0]=='Caseroot':
					timingProfileInfo['caseroot']=word[2]
				elif word[0]=='Timeroot':
					timingProfileInfo['timeroot']=word[2]
				elif word[0]=='User':
					timingProfileInfo['user']=word[2]
				elif word[0]=='Curr':
					timingProfileInfo['curr']=word[3]
				elif word[0]=='grid':
					timingProfileInfo['long_res']=word[2]
				elif word[0]=='compset':
					timingProfileInfo['long_compset']=word[2]
				elif word[0]=='stop_option':
					timingProfileInfo['stop_option']=word[2]
					newWord=word[3].split(" ")	
					timingProfileInfo['stop_n']=newWord[2]		
				elif word[0]=='run_length':
					newWord=word[3].split(" ")
					timingProfileInfo['run_length']=word[2]
				
			flagrun=False
			flaginit=False
			flagfinal=False
			word=line.split(None,1)
			if word[0]=='total':
				newWord=word[1].split(":")
				newWord1=newWord[1].split(" ")
				timingProfileInfo['total_pes']=newWord1[1]
			elif word[0]=='mpi':
				newWord=word[1].split(":")
				newWord1=newWord[1].split(" ")
				timingProfileInfo['mpi_task']=newWord1[1]
			elif word[0]=='pe':
				newWord=word[1].split(":")
				newWord1=newWord[1].split(" ")
				timingProfileInfo['pe_count']=newWord1[1]
			elif word[0]=='Model':
				newWord=word[1].split(":")
				newWord1=newWord[1].split()
				if 'model_cost' in timingProfileInfo.keys():
					timingProfileInfo['model_throughput']=newWord1[0]
				else:
					timingProfileInfo['model_cost']=newWord1[0]
			elif word[0]=='Actual':
				newWord=word[1].split(":")
				newWord1=newWord[1].split()
				timingProfileInfo['actual_ocn']=newWord1[0]
			elif word[0]=='Init' and flaginit == False:
				newWord=word[1].split(":")
				newWord1=newWord[1].split()
				timingProfileInfo['init_time']=newWord1[0]
				flaginit = True
			elif word[0]=='Run' and flagrun == False:
				newWord=word[1].split(":")
				newWord1=newWord[1].split()
				timingProfileInfo['run_time']=newWord1[0]
				flagrun = True
			elif word[0]=='Final' and flagfinal == False:
				newWord=word[1].split(":")
				newWord1=newWord[1].split()
				timingProfileInfo['final_time']=newWord1[0]
				flagfinal = True
			elif len(timingProfileInfo)>=20:
				break
	parseFile.close()
	duplicateFlag = checkDuplicateExp(timingProfileInfo['case'],timingProfileInfo['lid'],timingProfileInfo['user'])
	if duplicateFlag is True:
		return (True) # This skips this experiment and moves to next
	tablelist=[]
	
	if filename.endswith('.gz'):
		parseFile=gzip.open(filename,'rb')
	else:
		parseFile=open(filename,'rb')
	lines=parseFile.readlines()
	for i in range(16,25):
		tablelist.append(lines[i])	

	resultlist=tableParse(tablelist)
	word=[]
	for i in range(46,57):
		word=lines[i].split()
		if word[1]=='Run':
			runTimeTable.append(word[0])
		else:
			runTimeTable.append(str(word[0])+'_COMM')
		runTimeTable.append(word[3])
		runTimeTable.append(word[5])
		runTimeTable.append(word[7])	

	for i in range(9):
		tmpthread1=resultlist[i]['component']
		change1=tmpthread1.split(" ")
		componentTable.append(change1[0])
		componentTable.append(resultlist[i]['comp_pes'])
		componentTable.append(resultlist[i]['root_pe'])
		componentTable.append(resultlist[i]['tasks'])
		tmpthread=resultlist[i]['threads']
		change=tmpthread.split(" ")
		componentTable.append(change[1])
		componentTable.append(resultlist[i]['instances'])
		componentTable.append(resultlist[i]['stride'])
		
	parseFile.close()
	
	readmefile=gzip.open(readmefile,'rb')
	readmeparse = parseReadme(readmefile)
	readmefile.close()
	expversion = parseModelVersion(gitfile)
	new_experiment = Timingprofile(case=timingProfileInfo['case'],
					lid=timingProfileInfo['lid'],
					machine=timingProfileInfo['machine'],
					caseroot=timingProfileInfo['caseroot'],
					timeroot=timingProfileInfo['timeroot'],
					user=timingProfileInfo['user'],
					exp_date=changeDateTime(timingProfileInfo['curr']),
					long_res=timingProfileInfo['long_res'],
					res=readmeparse['res'],
					compset=readmeparse['compset'],
					long_compset=timingProfileInfo['long_compset'],
					stop_option=timingProfileInfo['stop_option'],
					stop_n=timingProfileInfo['stop_n'],
					run_length=timingProfileInfo['run_length'],
					total_pes_active=timingProfileInfo['total_pes'],
					mpi_tasks_per_node=timingProfileInfo['mpi_task'],
					pe_count_for_cost_estimate=timingProfileInfo['pe_count'],
					model_cost=timingProfileInfo['model_cost'],
					model_throughput=timingProfileInfo['model_throughput'],
					actual_ocn_init_wait_time=timingProfileInfo['actual_ocn'],
					init_time=timingProfileInfo['init_time'],
					run_time=timingProfileInfo['run_time'],
					final_time=timingProfileInfo['final_time'],
					version = expversion)
	db.session.add(new_experiment)

	# table has to have a same experiment id
	forexpid = Timingprofile.query.order_by(Timingprofile.expid.desc()).first()

	#insert pelayout
	i=0
	while i < len(componentTable):
		new_pelayout = Pelayout(expid=forexpid.expid,
					component=componentTable[i],
					comp_pes=componentTable[i+1],
					root_pe=componentTable[i+2],
					tasks=componentTable[i+3],
					threads=componentTable[i+4],
					instances=componentTable[i+5],
					stride=componentTable[i+6])
		db.session.add(new_pelayout)	
		i=i+7
	#insert run time
	i=0
	while i < len(runTimeTable):
		new_runtime = Runtime(expid=forexpid.expid,
					component=runTimeTable[i],
					seconds=runTimeTable[i+1],
					model_day=runTimeTable[i+2],
					model_years=runTimeTable[i+3])
		db.session.add(new_runtime)
		i=i+4
	# insert modelTiming
	insertTiming(timingfile,forexpid.expid,db)
	# store raw data (In server and Minio)
	zipFolder(forexpid.lid,forexpid.user,forexpid.expid,fpath)
	# try commit if not, flush 
	try:	
		db.session.commit()
	except:
		db.session.rollback()	
	return (True) 


def removeFolder(removeroot):
	try:
		shutil.rmtree(os.path.join(removeroot,'experiments'))
		os.remove(os.path.join(removeroot,'experiments.zip'))
	except OSError as e:
		return("Error: %s - %s." % (e.filename, e.strerror))
	
	return

def zipFolder(exptag,exptaguser,exptagid,fpath):
	newroot='/pace/assets/static/data/'
	expname=0	
	root=fpath
	for path, subdirs, files in os.walk(root):
		for name in subdirs:
			if name.startswith('CaseDocs.'+str(exptag)):
				expname = 'exp-'+exptaguser+'-'+str(exptagid)
				shutil.make_archive(os.path.join(newroot,expname),'zip',path)
				uploadMinio(newroot,expname)
	return

def uploadMinio(newroot,expname):
	from minio import Minio
	from minio.error import (ResponseError, BucketAlreadyOwnedByYou,BucketAlreadyExists)
	myAkey,mySkey, myMiniourl = getMiniokey()
	# Initialize minioClient with an endpoint and access/secret keys.
	minioClient = Minio(myMiniourl,access_key=myAkey,secret_key=mySkey,secure=True)
	try:
		minioClient.fput_object('e3sm', expname+'.zip', os.path.join(newroot,expname)+'.zip')
	except ResponseError as err:     
		print(err)

def insertTiming(mtFile,expID,db):
	sourceFile = tarfile.open(mtFile)
	for element in sourceFile:
		#to determine everything, this string is split two different ways:
		underScore = element.name.split("_")
		slash = element.name.split("/")
		if len(slash) == 2 and ( ("." in slash[1]) or underScore[len(underScore)-1] == "stats"):
			rankStr = ""
			if "." in slash[1]:
				#Check if all digits are zeros:
				zeroCount = 0
				rankStr = slash[1].split(".")[1]
				for i in range(len(rankStr)):
					if rankStr[i] == "0":
						zeroCount = zeroCount+1
				if zeroCount == len(rankStr):
					rankStr = "0"
			elif underScore[len(underScore)-1] == "stats":
				rankStr = underScore[len(underScore)-1]
			#This is a file we want! Let's save it:
			new_modeltiming = ModelTiming(expid=expID, jsonVal=mt.parse(sourceFile.extractfile(element)),rank=rankStr)
			db.session.add(new_modeltiming)
	
	return

if __name__ == "__main__":
	parseData()
