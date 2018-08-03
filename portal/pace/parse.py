import array
import sys,os
import gzip
import tarfile
import shutil
import zipfile
import pymysql
import mtDB as mt
from pace_common import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
#from datatest import Base, User, Experiment
from sqlalchemy import Column, ForeignKey, Integer, String, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship



def spaceConcat(phraseIn,subGroup = False,filter="\n\t"):
    phraseIn = phraseIn.strip(filter)
    #Destroy spaces by default:
    phraseSplit = phraseIn.split(" ")
    #print(phraseSplit)
    total=[""]
    currPhrase = 0
    onWord = False
    firstPhrase = True
    for i in range(len(phraseSplit)):
        if onWord or not phraseSplit[i] == "":
            if not onWord:
                onWord = True
                #print("On word")
                if not subGroup or not firstPhrase:
                    total.append("")
            firstPhrase = False
            addWord = True
            #Ignore newlines:
            if phraseSplit[i]  == "":
                #print("'"+phraseSplit[i] + "' | '" + phraseSplit[i+1]+"'")
                onWord = False
                addWord = False
                #print("Off word")
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
            #print "test: "+splitValues[i]
            tableColumn[names[i]] = splitValues[i].strip("(")
        resultList.append(tableColumn)
    return resultList

def createdatabase(filename):
	if filename.endswith('.gz'):
		parseFile=gzip.open(filename,'rb')
	else:
		parseFile=open(filename,'rb')	
	onetags=[]
	twotags=[]
	threetags=[]
	fourtags=[]
	timeProfileFlag=0
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
					onetags.append(word[2]+" "+newWord[0])
					timeProfileFlag=1
		
			word=line.split(None,1)
			#print(word[1])
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
				threetags.append(newWord1[0]+" "+newWord1[1])
			elif word[0]=='Actual':
				newWord=word[1].split(":")
				newWord1=newWord[1].split()
				threetags.append(newWord1[0]+" "+newWord1[1])
				timeProfileFlag+=1
			elif timeProfileFlag>=2:
				break
	parseFile.close()

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
		fourtags.append(word[0])
		fourtags.append(word[3])
		fourtags.append(word[5])
		fourtags.append(word[7])	

	for i in range(9):
		twotags.append(resultlist[i]['component'])
		twotags.append(resultlist[i]['comp_pes'])
		twotags.append(resultlist[i]['root_pe'])
		twotags.append(resultlist[i]['tasks'])
		twotags.append(resultlist[i]['threads'])
		twotags.append(resultlist[i]['instances'])
		twotags.append(resultlist[i]['stride'])
		
	parseFile.close()
	
	
	# Database work					
	Base = declarative_base() 
	 
	class Timingprofile(Base):
		__tablename__ = 'timing_profile'
		expid = Column(Integer, primary_key=True)    
		case = Column(String(250),nullable=False)
		lid = Column(String(250), nullable=False)
		machine = Column(String(250), nullable=False)
		caseroot = Column(String(250),nullable=False)	
		timeroot = Column(String(250),nullable=False)	
		user = Column(String(250),nullable=False)
		curr_date = Column(String(250),nullable=False)
		grid = Column(String(250),nullable=False)
		compset = Column(String(250),nullable=False)
		stop_option = Column(String(250),nullable=False)
		stop_n = Column(String(250),nullable=False)        
		run_length = Column(String(250), nullable=False)
		total_pes_active = Column(String(250), nullable=False)
		mpi_tasks_per_node = Column(String(250), nullable=False)
		pe_count_for_cost_estimate = Column(String(250), nullable=False)
		model_cost = Column(String(250), nullable=False)
		model_throughput = Column(String(250), nullable=False)
		actual_ocn_init_wait_time = Column(String(250), nullable=False)
	    	
	class Pelayout(Base):
		__tablename__ = 'pe_layout'
		id = Column(Integer, primary_key=True)
		expid=Column(Integer, nullable=False)
		component = Column(String(250), nullable=False)
		comp_pes = Column(String(250), nullable=False)
		root_pe = Column(String(250), nullable=False)
		tasks = Column(String(250), nullable=False)
		threads = Column(String(250), nullable=False)
		instances = Column(String(250), nullable=False)
		stride = Column(String(250), nullable=False)

	class Runtime(Base):
		__tablename__ = 'run_time'
		id = Column(Integer, primary_key=True)
		expid=Column(Integer, nullable=False)
		component = Column(String(250), nullable=False)
		seconds = Column(String(250), nullable=False)
		model_day = Column(String(250), nullable=False)
		model_years = Column(String(250), nullable=False)
	    
	
	dbConn,dbengine,dburl=connectDatabase()
	Base.metadata.create_all(dbengine)
	Base.metadata.bind = dbConn
	DBSession = sessionmaker(bind=dbConn)
	paceDB = DBSession()

	# Insert an experiment in the experiment table
	new_experiment = Timingprofile(case=onetags[0],lid=onetags[1],machine=onetags[2],caseroot=onetags[3],timeroot=onetags[4],user=onetags[5],curr_date=onetags[6],grid=onetags[7],compset=onetags[8],stop_option=onetags[9],stop_n=onetags[10],run_length=onetags[11],total_pes_active=threetags[0],mpi_tasks_per_node=threetags[1],pe_count_for_cost_estimate=threetags[2],model_cost=threetags[3],model_throughput=threetags[4],actual_ocn_init_wait_time=threetags[5])
	paceDB.add(new_experiment)

	# table has to have a same experiment id
	forexpid = paceDB.query(Timingprofile).order_by(Timingprofile.expid.desc()).first()

	#insert pelayout
	i=0
	while i < len(twotags):
		new_pelayout = Pelayout(expid=forexpid.expid,component=twotags[i],comp_pes=twotags[i+1],root_pe=twotags[i+2],tasks=twotags[i+3],threads=twotags[i+4],instances=twotags[i+5],stride=twotags[i+6])
		paceDB.add(new_pelayout)	
		i=i+7
	#insert run time
	i=0
	while i < len(fourtags):
		new_runtime = Runtime(expid=forexpid.expid,component=fourtags[i],seconds=fourtags[i+1],model_day=fourtags[i+2],model_years=fourtags[i+3])
		paceDB.add(new_runtime)
		i=i+4
	paceDB.commit()
	

	print("-------------------------Stored-in-Database-------------------------------")
	return (onetags[1],forexpid.expid)

def parseData():
	# start main
	#first unzip uploaded file
	fpath='/pace/prod/portal/upload'
	zip_ref=zipfile.ZipFile('/pace/prod/portal/upload/experiments.zip','r')
	zip_ref.extractall(fpath)
	zip_ref.close

	# list and store path of all new uploaded file
	dic=[]
	for i in os.listdir(fpath):
		 dic.append(os.path.join(fpath,i))


	# untar all tar files
	for i in range(len(dic)):
		if dic[i].endswith('.tar.gz'):
			tar = tarfile.open(dic[i])
			tar.extractall()
			tar.close()

	# store path of all directories
	dic1=[]
	for i in os.listdir(fpath):
		if i !='parse.py' and i!='upload' and i!='experiments.zip':	
			dic1.append(i)


	# go through all directories and store timing profile file only
	allfile=[]
	timingfile=[]
	for i in range(len(dic1)):
		root=os.path.join(fpath,dic1[i])
		for path, subdirs, files in os.walk(root):
			for name in files:
				if name.startswith("timing."):
					timingfile.append(os.path.join(path, name))
				if name.startswith("e3sm_timing."):		
					allfile.append(os.path.join(path, name))


	# parse and store timing profile file in a database
	exptag=[]
	for i in range(len(allfile)):
		a,b=createdatabase(allfile[i])
		mt.insert(timingfile[i],b)	
		exptag.append(a)

	newroot='/pace/assets/static/data/'
	# zip successfull experiments into folder experiments
	for i in range(len(exptag)):
		root=fpath
		for path, subdirs, files in os.walk(root):
			for name in subdirs:
				if name.startswith(exptag[i]):
					shutil.make_archive(os.path.join(newroot,'experiment-'+exptag[i]),'zip',os.path.join(path, name))

	removeroot='/pace/prod/portal/upload/'
	# remove data
	try:
		shutil.rmtree(os.path.join(removeroot,'experiments'))
		os.remove(os.path.join(removeroot,'experiments.zip'))
	except OSError as e:
		print("Error: %s - %s." % (e.filename, e.strerror))


if __name__ == "__main__":
	parseData()
