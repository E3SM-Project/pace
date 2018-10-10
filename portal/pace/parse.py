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
	
	# list of lid from experiments
	exptag=[]
	exptaguser=[]
	exptagid=[]
	# parse and store timing profile file in a database
	for i in range(len(allfile)):
		# to store lid after parsing, or is 'duplicate' 
		lid=0
		# to store expid after parsing
		duplicateExp=False
		# parse  'e3sm_timing.' and 'README.case.', returns lid,expid for unique experiments else 'duplicate,0'
		lid,expuser,expid,duplicateExp=insertExperiment(allfile[i],readmefile[i],timingfile[i],gitdescribefile[i],db)
		
		if duplicateExp == False:
			# append lid to list 
			exptag.append(lid)
			exptaguser.append(expuser)
			exptagid.append(expid)
			print("-----------------Stored-in-Database-------------------")
	# try commit if not, flush 
	try:	
		db.session.commit()
	except:
		db.session.rollback()
	# zip successfull experiments into folder experiments
	zipFolder(exptag,exptaguser,exptagid,fpath)
	# remove uploaded experiments
	removeFolder(tmp_updir)
	

	return('File Upload and Stored in Database Success')

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

def parseGitfile(gitfile):
	parsefile = gzip.open(gitfile,'rb')
	version = 0
	for line in parsefile:
		version = line.strip('\n')
		break
	parsefile.close()
	return version

def insertExperiment(filename,readmefile,timingfile,gitfile,db):
	if filename.endswith('.gz'):
		parseFile=gzip.open(filename,'rb')
	else:
		parseFile=open(filename,'rb')	
	onetags=[]
	twotags=[]
	threetags=[]
	fourtags=[]
	timeProfileFlag=0
	duplicateFlag=False
	word=''
	for line in parseFile:
		if line!='\n':
			if timeProfileFlag==0:		
				word=line.split(None,3)
				if word[0]=='Case':
					onetags.append(word[2])
				elif word[0]=='LID':
					onetags.append(word[2])
				elif word[0]=='Machine':
					onetags.append(word[2])
				elif word[0]=='Caseroot':
					onetags.append(word[2])
				elif word[0]=='Timeroot':
					onetags.append(word[2])
				elif word[0]=='User':
					onetags.append(word[2])
				elif word[0]=='Curr':
					onetags.append(word[3])
				elif word[0]=='grid':
					onetags.append(word[2])
				elif word[0]=='compset':
					onetags.append(word[2])
				elif word[0]=='stop_option':
					onetags.append(word[2])
					newWord=word[3].split(" ")
					onetags.append(newWord[2])			
				elif word[0]=='run_length':
					newWord=word[3].split(" ")
					onetags.append(word[2])
					timeProfileFlag=1
			flagrun=False
			flaginit=False
			flagfinal=False
			word=line.split(None,1)
			if word[0]=='total':
				newWord=word[1].split(":")
				newWord1=newWord[1].split(" ")
				threetags.append(newWord1[1])
			elif word[0]=='mpi':
				newWord=word[1].split(":")
				newWord1=newWord[1].split(" ")
				threetags.append(newWord1[1])
			elif word[0]=='pe':
				newWord=word[1].split(":")
				newWord1=newWord[1].split(" ")
				threetags.append(newWord1[1])
			elif word[0]=='Model':
				newWord=word[1].split(":")
				newWord1=newWord[1].split()
				threetags.append(newWord1[0])
			elif word[0]=='Actual':
				newWord=word[1].split(":")
				newWord1=newWord[1].split()
				threetags.append(newWord1[0])
				timeProfileFlag+=1
			elif word[0]=='Init' and flaginit == False:
				newWord=word[1].split(":")
				newWord1=newWord[1].split()
				threetags.append(newWord1[0])
				flaginit = True
			elif word[0]=='Run' and flagrun == False:
				newWord=word[1].split(":")
				newWord1=newWord[1].split()
				threetags.append(newWord1[0])
				flagrun = True
			elif word[0]=='Final' and flagfinal == False:
				newWord=word[1].split(":")
				newWord1=newWord[1].split()
				threetags.append(newWord1[0])
				flagfinal = True
			elif timeProfileFlag>=2:
				break
	parseFile.close()
	duplicateFlag = checkDuplicateExp(onetags[0],onetags[1],onetags[5])
	if duplicateFlag is True:
		return (onetags[1],onetags[5],0,True)
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
			fourtags.append(word[0])
		else:
			fourtags.append(str(word[0])+'_COMM')
		fourtags.append(word[3])
		fourtags.append(word[5])
		fourtags.append(word[7])	

	for i in range(9):
		tmpthread1=resultlist[i]['component']
		change1=tmpthread1.split(" ")
		twotags.append(change1[0])
		twotags.append(resultlist[i]['comp_pes'])
		twotags.append(resultlist[i]['root_pe'])
		twotags.append(resultlist[i]['tasks'])
		tmpthread=resultlist[i]['threads']
		change=tmpthread.split(" ")
		twotags.append(change[1])
		twotags.append(resultlist[i]['instances'])
		twotags.append(resultlist[i]['stride'])
		
	parseFile.close()
	
	readmefile=gzip.open(readmefile,'rb')
	readmeparse = parseReadme(readmefile)
	readmefile.close()
	expversion = parseGitfile(gitfile)
	new_experiment = Timingprofile(case=onetags[0],lid=onetags[1],machine=onetags[2],caseroot=onetags[3],timeroot=onetags[4],user=onetags[5],exp_date=changeDateTime(onetags[6]),long_res=onetags[7],res=readmeparse['res'],compset=readmeparse['compset'],long_compset=onetags[8],stop_option=onetags[9],stop_n=onetags[10],run_length=onetags[11],total_pes_active=threetags[0],mpi_tasks_per_node=threetags[1],pe_count_for_cost_estimate=threetags[2],model_cost=threetags[3],model_throughput=threetags[4],actual_ocn_init_wait_time=threetags[5],init_time=threetags[6],run_time=threetags[7],final_time=threetags[8],version = expversion)
	db.session.add(new_experiment)

	# table has to have a same experiment id
	
	forexpid = Timingprofile.query.order_by(Timingprofile.expid.desc()).first()

	#insert pelayout
	i=0
	while i < len(twotags):
		new_pelayout = Pelayout(expid=forexpid.expid, component=twotags[i],comp_pes=twotags[i+1],root_pe=twotags[i+2],tasks=twotags[i+3],threads=twotags[i+4],instances=twotags[i+5],stride=twotags[i+6])
		db.session.add(new_pelayout)	
		i=i+7
	#insert run time
	i=0
	while i < len(fourtags):
		new_runtime = Runtime(expid=forexpid.expid,component=fourtags[i],seconds=fourtags[i+1],model_day=fourtags[i+2],model_years=fourtags[i+3])
		db.session.add(new_runtime)
		i=i+4

	insertTiming(timingfile,forexpid.expid,db)
	return (onetags[1],onetags[5],forexpid.expid,False)


def removeFolder(removeroot):
	try:
		shutil.rmtree(os.path.join(removeroot,'experiments'))
		os.remove(os.path.join(removeroot,'experiments.zip'))
	except OSError as e:
		return("Error: %s - %s." % (e.filename, e.strerror))
	
	return

def zipFolder(exptag,exptaguser,exptagid,fpath):
	newroot='/pace/assets/static/data/'	
	for i in range(len(exptag)):
		root=fpath
		for path, subdirs, files in os.walk(root):
			for name in subdirs:
				if name.startswith('CaseDocs.'+str(exptag[i])):
					shutil.make_archive(os.path.join(newroot,'exp-'+exptaguser[i]+'-'+str(exptagid[i])),'zip',path)
	return

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
