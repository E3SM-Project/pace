# imports
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
from minio import Minio
from minio.error import (ResponseError, BucketAlreadyOwnedByYou,BucketAlreadyExists)

PACE_LOG_DIR,EXP_DIR,UPLOAD_FOLDER = getDirectories()

# main
def parseData(zipfilename,uploaduser):
	# open file to write pace report
	old_stdout = sys.stdout
	logfilename = 'pace-'+str(uploaduser)+'-'+str(datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))+'.log'
	logfile = PACE_LOG_DIR + logfilename
	log_file = open(logfile,'w')
	sys.stdout = log_file
	print ("* * * * * * * * * * * * * * PACE Report * * * * * * * * * * * * * *")
	try:	
		fpath=UPLOAD_FOLDER
		# Extract aggregated zip files
		zip_ref=zipfile.ZipFile(os.path.join(fpath,zipfilename),'r')
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
		tmpfilename = zipfilename.split('.')[0]
		for i in os.listdir(fpath):
			if i == tmpfilename:	
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
		print ('[ERROR]: %s' % e.strerror)
		removeFolder(UPLOAD_FOLDER,zipfilename)
		sys.stdout = old_stdout
		log_file.close()
		return ('ERROR/'+str(logfilename))
	except OSError as e:
		print ('[ERROR]: %s' % e.strerror)
		removeFolder(UPLOAD_FOLDER,zipfilename)
		sys.stdout = old_stdout
		log_file.close()
		return ('ERROR/'+str(logfilename))
	# boolean list
	isSuccess=[]
	# parse and store timing profile file in a database
	for i in range(len(allfile)):
		print (' ')
		print ('**************************************************')
		# insert experiments for given files
		isSuccess.append(insertExperiment(allfile[i],readmefile[i],timingfile[i],gitdescribefile[i],db,fpath, uploaduser))
		print ('**************************************************')
		print (' ')
	
	# remove uploaded experiments
	removeFolder(UPLOAD_FOLDER,zipfilename)
	sys.stdout = old_stdout
	log_file.close()
	# check parse status, returns status with report
	if False in isSuccess:
		return('fail/'+str(logfilename))
	else:
		return('success/'+str(logfilename))

# removes unwanted spaces (dedicated for parsing model_timing files)
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

# Returns a list of items from the table.
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

# change string into date time format
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

# converts path string into single file name (/home/absd/asde/file.txt -> file.txt)
def convertPathtofile(path):
	if '/' in path:
		foldername = path.split('/')
		return (foldername[len(foldername)-1]) #grab the last file from path link
	else:
		return path

# function to check duplicate experiments (check based on user,machinr,exp_date,case)
def checkDuplicateExp(euser,emachine,ecurr, ecase):
	eexp_date = changeDateTime(ecurr)
	flag=E3SMexp.query.filter_by(user=euser,machine=emachine,case=ecase,exp_date=eexp_date ).first()
	if flag is None:
		return(False)
	else:
		return(True)

# parser for readme file
def parseReadme(readmefilename):
	# open file
	if readmefilename.endswith('.gz'):
		fileIn=gzip.open(readmefilename,'rb')
	else:
		fileIn = open(readmefilename,'rb')
	resultElement = {}
	commandLine = None
	flag=False
	try:	
		for commandLine in fileIn:
			word=commandLine.split(" ")
			for element in word:
				# this line holds profile information
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
			# job done after finding elements res, compset
			if 'res' and 'compset' in resultElement.keys():		
				break
		# this case only runs if element 'res','compset' exists else throws keyError
		if resultElement['res'] is None:
			resultElement['res'] = 'nan'
		if resultElement['compset'] is None:
			resultElement['compset'] = 'nan'
	except KeyError as e:
		print ('[ERROR]: %s not found in %s' %(e,convertPathtofile(readmefilename)))
		fileIn.close()
		return False
	except IndexError as e:
		print ('[ERROR]: %s in file %s' %(e,convertPathtofile(readmefilename)))
		fileIn.close()		
		return False
	except :
		print ('    ERROR: Something is worng with %s' %convertPathtofile(readmefilename))
		fileIn.close()
		return False
	fileIn.close()	
	return resultElement

# parser for GIT_DESCRIBE file
def parseModelVersion(gitfile):
	# open file
	if gitfile.endswith('.gz'):
		parsefile = gzip.open(gitfile,'rb')
	else:
		parsefile = open(gitfile, 'rb')
	# initialize version
	version = 0
	for line in parsefile:
		if line != '\n':
			version = line.strip('\n')
			break
	parsefile.close()
	return version

# This function provides pathway to files for their respective parser function and finally stores in database
def insertExperiment(filename,readmefile,timingfile,gitfile,db,fpath, uploaduser):

	# returns expid if success else returns False
	forexpid = parseE3SMtiming(filename,readmefile,gitfile,db,fpath, uploaduser)
	if forexpid == False:
		return False
	print ('* Parsing: '+ convertPathtofile(timingfile))

	# insert modelTiming
	isSuccess = insertTiming(timingfile,forexpid.expid,db)
	if isSuccess == False:
		return False	
	print ('    -Complete')

	# store raw data (In server and Minio)
	print ('* Storing Experiment in file server')
	isSuccess = zipFolder(forexpid.lid,forexpid.user,forexpid.expid,fpath)
	if isSuccess == False:
		return False	
	print ('    -Complete')

	# try commit if not, rollback
	print ('* Storing Experiment Data in Database') 
	try:	
		db.session.commit()
		print ('    -Complete')
	except:
		db.session.rollback()

	# write basic summary in report
	print (' ')
	print ('----- Experiment Summary -----')
	print ('- Experiment ID (ExpID): '+str(forexpid.expid))
	print ('- User: '+str(forexpid.user))
	print ('- Machine: '+str(forexpid.machine))
	print ('- Web Link: '+str('https://pace.ornl.gov/exp-details/')+str(forexpid.expid))
	print ('------------------------------')
	print (' ')
	# close session	
	db.session.close()
	return (True) 

# parse e3sm files
def parseE3SMtiming(filename,readmefile,gitfile,db,fpath, uploaduser):
	# open file
	if filename.endswith('.gz'):
		parseFile=gzip.open(filename,'rb')
	else:
		parseFile=open(filename,'rb')

	# dictionary to store timingprofile 	
	timingProfileInfo={}
	# list to store component table
	componentTable=[]
	# list to store runtime table
	runTimeTable=[]
	# boolean flag
	duplicateFlag=False
	# tmp var for parsing purpose
	word=''
	print ('* Parsing: '+convertPathtofile(filename))
	try:
		for line in parseFile:
			if line!='\n':
				# find values for given keys
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

		# check if this is duplicate experiment 
		duplicateFlag = checkDuplicateExp(timingProfileInfo['user'],timingProfileInfo['machine'],timingProfileInfo['curr'],timingProfileInfo['case'])
		if duplicateFlag is True:
			print ('    -[Warining]: Duplicate Experiment, ' + convertPathtofile(filename))
			db.session.close()
			return (False) # This skips this experiment and moves to next
	
	except IndexError as e:
		print ('    ERROR: %s' %e)
		parseFile.close()
		return (False) # skips this experiment
	except KeyError as e:
		print ('    ERROR: Missing data %s' %e)
		parseFile.close()
		return (False) # skips this experiment
	except :
		print ('    ERROR: Something is worng with %s' %convertPathtofile(filename))
		parseFile.close()
		return (False) # skips this experiment	

	parseFile.close()
	
	# open file again to parse component and runtime tables
	try:
		if filename.endswith('.gz'):
			parseFile=gzip.open(filename,'rb')
		else:
			parseFile=open(filename,'rb')
		lines=parseFile.readlines()
		componentTableSuccess = False
		runtimeTableSuccess = False
		component=[]
		tablelist=[]
		# loop to grab component and store in a list and parse runtime table
		for i in range(len(lines)):
			if lines[i] != '\n':
				firstWord = lines[i].split()[0]
				if firstWord == 'component':
					for j in range(9):
						tablelist.append(lines[i+j+2])
					componentTableSuccess = True
				# parse runtime table and store in a list
				elif firstWord == 'TOT':
					for j in range(11):	
						component=lines[i+j].split()
						if component[1]=='Run':
							runTimeTable.append(component[0])
						else:
							runTimeTable.append(str(component[0])+'_COMM')
						runTimeTable.append(component[3])
						runTimeTable.append(component[5])
						runTimeTable.append(component[7])
						runtimeTableSuccess = True
			# grabbed both tables then break
			if componentTableSuccess == True and runtimeTableSuccess == True:
				break
		# check if both table exists
		if componentTableSuccess != True or runtimeTableSuccess != True:
			print ('    ERROR: runtime/component table not found')
			return False

		# parse component table
		resultlist=tableParse(tablelist)
		parseFile.close()
		
		# store component table values in a list
		for i in range(len(tablelist)):
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
	
		print ('    -Complete')

		# parse README.docs file
		print ('* Parsing: '+convertPathtofile(readmefile))
		readmeparse = parseReadme(readmefile)
		if readmeparse == False:
			return (False) #this skips the experiment
		print ('    -Complete')

		# parse GIT_DESCRIBE file
		print ('* Parsing: '+convertPathtofile(gitfile))
		expversion = parseModelVersion(gitfile)
		print ('    -Complete')

		# insert timingprofile 
		new_experiment = E3SMexp(case=timingProfileInfo['case'],
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
						version = expversion,
						upload_by = uploaduser)
		db.session.add(new_experiment)

		# table has to have a same experiment id
		forexpid = E3SMexp.query.order_by(E3SMexp.expid.desc()).first()

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
		return (forexpid)
	except IndexError as e:
		print ('    ERROR: %s' %e)
		parseFile.close()
		return (False) # skips this experiment
	except KeyError as e:
		print ('    ERROR: Missing data %s' %e)
		parseFile.close()
		return (False) # skips this experiment
	except :
		print ('    ERROR: Something is worng with %s' %convertPathtofile(filename))
		db.session.rollback()
		parseFile.close()
		return (False) # skips this experiment	

# removes temporary folders in server
def removeFolder(removeroot,filename):
	try:
		shutil.rmtree(os.path.join(removeroot,filename.split('.')[0]))
		os.remove(os.path.join(removeroot,filename))
	except OSError as e:
		print ("    Error: %s - %s." % (e.filename, e.strerror))
	
	return

# aggregate files and store in file server
def zipFolder(exptag,exptaguser,exptagid,fpath):
	try:	
		expname=0	
		root=fpath
		for path, subdirs, files in os.walk(root):
			for name in subdirs:
				if name.startswith('CaseDocs.'+str(exptag)):
					expname = 'exp-'+exptaguser+'-'+str(exptagid)
					shutil.make_archive(os.path.join(EXP_DIR,expname),'zip',path)
					# upload files into file server
					isSuccess=uploadMinio(EXP_DIR,expname)
					if isSuccess == False:
						return False
	except IOError as e:
		print ('    ERROR: %s' %e)
		return False	
	return True

# function to store files into file server
def uploadMinio(EXP_DIR,expname):
	# get minio credentials 
	myAkey,mySkey, myMiniourl = getMiniokey()
	# Initialize minioClient with an endpoint and access/secret keys.
	minioSecure=True
	if os.getenv("PACE_DOCKER_INSTANCE"):
		minioSecure=False
	minioClient = Minio(myMiniourl,access_key=myAkey,secret_key=mySkey,secure=minioSecure)
	try:
		if not minioClient.bucket_exists("e3sm"):
			minioClient.make_bucket("e3sm")
		minioClient.fput_object('e3sm', expname+'.zip', os.path.join(EXP_DIR,expname)+'.zip')
	except ResponseError as err:     
		print('    ERROR: Failed to upload to file server %s' %err)
		return (False)
	return True

# parse model_timing files
def insertTiming(mtFile,expID,db):
	try:
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
	except IndexError as e:
		print ('    ERROR: %s' %e)
		parseFile.close()
		return (False) # skips this experiment
	except KeyError as e:
		print ('    ERROR: Missing data %s' %e)
		parseFile.close()
		return (False) # skips this experiment
	except :
		print ('    ERROR: Something is worng with %s' %convertPathtofile(mtFile))
		db.session.rollback()
		parseFile.close()
		return (False) # skips this experiment	
	return

if __name__ == "__main__":
	parseData(filename,user)
