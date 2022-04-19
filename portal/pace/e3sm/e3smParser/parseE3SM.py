#! /usr/bin/env python3
# @file parse.py
# @brief initial flow process for parsing.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13
# imports
from pace.e3sm.e3smDb.datastructs import *
from pace.pace_common import *
import sys,os
import tarfile
import shutil
import zipfile
from pace.e3sm.e3smParser import parseModelTiming
from minio import Minio
#from minio.error import (ResponseError, BucketAlreadyOwnedByYou,BucketAlreadyExists)
from minio.error import (InvalidResponseError)
from sqlalchemy.exc import SQLAlchemyError
import json

import tarfile
import codecs
from os.path import abspath, realpath, dirname, join as joinpath
from sys import stderr
#from . import inputFileParser
from pace.e3sm.e3smParser import parseE3SMTiming
from pace.e3sm.e3smParser import parseModelVersion
from pace.e3sm.e3smParser import parseReadMe
from pace.e3sm.e3smParser import parseMemoryProfile
from pace.e3sm.e3smParser import parseScorpioStats
from pace.e3sm.e3smParser import parseCaseDocs
from pace.e3sm.e3smParser import parseBuildTime

resolved = lambda x: realpath(abspath(x))

def badpath(path, base):
    # joinpath will ignore base if path is absolute
    return not resolved(joinpath(base,path)).startswith(base)

def badlink(info, base):
    # Links are interpreted relative to the directory containing the link
    tip = resolved(joinpath(base, dirname(info.name)))
    return badpath(info.linkname, base=tip)

def safemembers(members):
    base = resolved(".")

    for finfo in members:
        if badpath(finfo.name, base):
            print(finfo.name, "is blocked (illegal path)",file=stderr)
        elif finfo.issym() and badlink(finfo,base):
            print(finfo.name, "is blocked: Hard link to", finfo.linkname,file=stderr)
        elif finfo.islnk() and badlink(finfo,base):
            print(finfo.name, "is blocked: Symlink to", finfo.linkname, file=stderr)
        else:
            yield finfo

PACE_LOG_DIR,EXP_DIR,UPLOAD_FOLDER = getDirectories()

#need here
# main
def parseData(zipfilename,uploaduser):
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
                tar.extractall(members=safemembers(tar))
                tar.close()

        # store path of all directorie
        dic1=[]
        tmpfilename = zipfilename.split('.')[0]
        for i in os.listdir(fpath):
            if i == tmpfilename:
                dic1.append(i)

        # get dir for each experiments
        experimentDirs = []
        for i in range(len(dic1)):
            for dir in os.listdir(os.path.join(fpath,dic1[i])):
                if dir.startswith('exp'):
                    experimentDirs.append(os.path.join(fpath,tmpfilename,dir))
        
        # go through all directories and grab certain files for parsing
        experimentFiles = []
        for root in experimentDirs:
            model = {
                "timingfile":None,
                "allfile":None,
                "readmefile":None,
                "gitdescribefile":None,
                "scorpiofile":None,
                "memoryfile":None,
                "casedocs":None,
                "buildtimefile":None
            }
            for path, subdirs, files in os.walk(root):
                for name in files:
                    if name.startswith("timing."):
                        model['timingfile'] = os.path.join(path, name)
                    elif name.startswith("e3sm_timing."):
                        model['allfile'] = os.path.join(path, name)
                    elif name.startswith("README.case."):
                        model['readmefile'] = os.path.join(path, name)
                    elif name.startswith("GIT_DESCRIBE."):
                        model['gitdescribefile'] = os.path.join(path, name)
                    elif name.startswith("spio_stats."):
                        model['scorpiofile'] = os.path.join(path, name)
                    elif name.startswith("memory."):
                        model['memoryfile'] = os.path.join(path, name)
                    elif name.startswith("build_times.txt."):
                        model['buildtimefile'] = os.path.join(path, name)
                for name in subdirs:
                    if name.startswith("CaseDocs."):
                        model['casedocs'] = os.path.join(path, name)
            experimentFiles.append(model)

        # boolean list
        isSuccess=[]
        # parse and store timing profile file in a database
        for index in range(len(experimentFiles)):
            print (' ')
            print ('**************************************************')
            # insert experiments for given files
            isSuccess.append(insertExperiment(experimentFiles[index]['allfile'],
                                            experimentFiles[index]['readmefile'],
                                            experimentFiles[index]['timingfile'],
                                            experimentFiles[index]['gitdescribefile'],
                                            experimentFiles[index]['scorpiofile'],
                                            experimentFiles[index]['memoryfile'],
                                            experimentFiles[index]['casedocs'],
                                            experimentFiles[index]['buildtimefile'],
                                            db,fpath,uploaduser))
            print ('**************************************************')
            print (' ')
        # remove uploaded experiments
        removeFolder(UPLOAD_FOLDER,zipfilename)

        # check parse status, returns status with report
        if False in isSuccess:
            return('fail')
        else:
            return('success')
    except IOError as e:
        print(('[ERROR]: %s' % e.strerror))
        # NOTE: DO NOT use removeFolder without validating zipfilename
        # Cybersecurity issue
        # removeFolder(UPLOAD_FOLDER,zipfilename)
        return ('ERROR')
    except OSError as e:
        print(('[ERROR]: %s' % e.strerror))
        # removeFolder(UPLOAD_FOLDER,zipfilename)
        return ('ERROR')
    except Exception as e:
        print(('[ERROR]: %s' %e))
        print(('[ERROR]: Other error during upload'))
        # removeFolder(UPLOAD_FOLDER,zipfilename)
        return ('ERROR')

#need here
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

#need here
# converts path string into single file name (/home/absd/asde/file.txt -> file.txt)
def convertPathtofile(path):
    if not path:
        return ("None")
    if '/' in path:
        foldername = path.split('/')
        return (foldername[len(foldername)-1]) #grab the last file from path link
    return path

#need here
# function to check duplicate experiments (check based on user,machinr,exp_date,case)
# Returns (True, expid) if duplicate exists, else (False, None)
def checkDuplicateExp(euser,emachine,ecurr, ecase):
    eexp_date = changeDateTime(ecurr)
    exp=E3SMexp.query.filter_by(user=euser,machine=emachine,case=ecase,exp_date=eexp_date ).first()
    if exp is None:
        return(False,None)
    else:
        return(True,exp.expid)

#need here
def insertMemoryFile(memfile,db,expid):
    data = None
    if memfile:
        data = parseMemoryProfile.loaddb_memfile(memfile)
        if not data:
            print("Empty memory profile file")
            return True
    else:
        print("No memory profile file")
        return True
    name = 'memory'
    mem = db.session.query(MemfileInputs).filter_by(expid=expid, name=name).first()
    if mem:
        print("Insertion is discarded due to duplication: expid=%d, name=%s" % (expid, name))
        return True
    else:
        mem = MemfileInputs(expid=expid, name=name, data=data)
        db.session.add(mem)
    return True

#need here
def insertScorpioStats(spiofile,db,expid,runTime):
    #TODO
    if spiofile:
        data = parseScorpioStats.loaddb_scorpio_stats(spiofile,runTime)
        if not data:
            print('Empty scorpio io stats file')
            return True
        else:
            for model in data:
                spio = db.session.query(ScorpioStats).filter_by(expid=expid, name=model['name']).first()
                if spio:
                    print("Insertion in scorpio is discarded due to duplication: expid=%d, name=%s" % (expid, model['name']))
                else:
                    spio = ScorpioStats(expid=expid, name=model['name'], data=model['data'],iopercent=model['iopercent'],iotime=model['iotime'])
                    db.session.add(spio)
    else:
        print('Scorpio IO file not found')
    return True

def insertBuildTimeFile(buildtimefile,db,expid):
    if buildtimefile:
        data, total_computecost, total_walltime = parseBuildTime.loaddb_buildTimesFile(buildtimefile)
        if not data:
            print("Empty file")
            return True
        if total_walltime == 0:
            total_walltime = None
    else:
        print("No file")
        return True
    buildtime = db.session.query(BuildTime).filter_by(expid=expid).first()
    if buildtime:
        print("Insertion is discarded due to duplication: expid=%d" % (expid))
        return True
    else:
        buildtime = BuildTime(expid=expid, data=json.dumps(data), total_computecost=total_computecost, total_walltime = total_walltime)
        db.session.add(buildtime)
    return True

#need here
# This function provides pathway to files for their respective parser function and finally stores in database
def insertExperiment(filename,readmefile,timingfile,gitfile,
                    spiofile,memfile,casedocs,buildtimefile,
                    db,fpath,uploaduser):
    # returns True if successful or if duplicate exp already in database
    (successFlag, duplicateFlag, currExpObj) = insertE3SMTiming(filename,readmefile,gitfile,db,fpath,uploaduser)
    # If this is a duplicate experiment, return True as we won't need to parse rest of this exp files
    if duplicateFlag == True:
        return True
    if successFlag == False:
        return False
    print(('* Parsing model timing file :'+ convertPathtofile(timingfile)))

    # insert modelTiming
    isSuccess = insertTiming(timingfile,currExpObj.expid,db)
    if isSuccess == False:
        return False
    print('    -Complete')

    #insert memory file
    #TODO create a seperate function to handle logic and db insertion
    print(('* Parsing meomory file : '+ convertPathtofile(memfile)))
    isSuccess = insertMemoryFile(memfile,db,currExpObj.expid)
    if not isSuccess:
        return False
    print('    -Complete')


    #insert scorpio stats
    #TODO create a seperate function to handle logic and db insertion
    print(('* Parsing scorpio io stats file : '+ convertPathtofile(spiofile)))
    isSuccess = insertScorpioStats(spiofile,db,currExpObj.expid, currExpObj.run_time)
    if not isSuccess:
        return False
    print('    -Complete')

    #insert casedocs files (namelist, rc, xml)
    #TODO
    print(('* Parsing casedocs file : '+ convertPathtofile(casedocs)))
    isSuccess = parseCaseDocs.loaddb_casedocs(casedocs,db,currExpObj)
    if not isSuccess:
        return False
    print('    -Complete')

    #insert build time
    print(('* Parsing build time file : '+ convertPathtofile(buildtimefile)))
    isSuccess = insertBuildTimeFile(buildtimefile,db,currExpObj.expid)
    if not isSuccess:
        return False
    print('    -Complete')

    # store raw data (In server and Minio)
    print('* Storing Experiment in file server')
    (isSuccess,zipFileFullPath) = zipFolder(currExpObj.lid,currExpObj.user,currExpObj.expid,fpath)
    if isSuccess == False:
        return False
    print('    -Complete')
    

    # try commit if not, rollback
    print('* Storing Experiment Data in Database')

    try:
        db.session.commit()
        print('    -Complete')
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        print(('    SQL ERROR: %s' %e))
        db.session.rollback()
        return False # skips this experiment
    except Exception as e:
        print(('[ERROR]: %s' %e))
        db.session.rollback()
        return False # skips this experiment

    # write basic summary in report
    print(' ')
    print('----- Experiment Summary -----')
    print(('- Experiment ID (ExpID): '+str(currExpObj.expid)))
    print(('- User: '+str(currExpObj.user)))
    print(('- Machine: '+str(currExpObj.machine)))
    print(('- Web Link: '+str('https://pace.ornl.gov/exp-details/')+str(currExpObj.expid)))
    print('------------------------------')
    print(' ')

    # close session
    db.session.close()
    
    return True

#need here
# Parse e3sm files
def insertE3SMTiming(filename,readmefile,gitfile,db,fpath, uploaduser):
    try:
        
        # parse e3sm_timing.* file
        print(('* Parsing e3sm_timing file: '+convertPathtofile(filename)))
        successFlag, timingProfileInfo, componentTable, runTimeTable = parseE3SMTiming.parseE3SMtiming(filename)
        if not successFlag:
            return (successFlag, False, None)
        
        #check for duplicate experiments
        (duplicateFlag, existingExpid) = checkDuplicateExp(timingProfileInfo['user'],timingProfileInfo['machine'],timingProfileInfo['curr'],timingProfileInfo['case'])
        if duplicateFlag is True:
            print(('    -[NOTE]: Duplicate of Experiment : ' + str(existingExpid) ))
            db.session.close()
            # Set success to True as the experiment already exists in database
            successFlag = True
            return (successFlag, duplicateFlag, None) # This skips this experiment and moves to next

        print('     -Complete')

        # parse README.docs file
        print(('* Parsing README.docs file : '+convertPathtofile(readmefile)))
        readmeparse = parseReadMe.parseReadme(readmefile)
        if readmeparse == False:
            return (successFlag, duplicateFlag, None) #this skips the experiment
        print('    -Complete')

        # parse GIT_DESCRIBE file
        print(('* Parsing GIT_DESCRIBE file : '+convertPathtofile(gitfile)))
        expversion = parseModelVersion.parseModelVersion(gitfile)
        print('    -Complete')

        
        # insert timingprofile
        new_e3sm_experiment = E3SMexp(case=timingProfileInfo['case'],
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
                        upload_by = uploaduser,
                        case_group = None)
        db.session.add(new_e3sm_experiment)
        # table has to have a same experiment id
        currExpObj = E3SMexp.query.order_by(E3SMexp.expid.desc()).first()
        # Following direct sql query returns already committed data in database and not the current exp being added
        # myexpid = db.engine.execute("select expid from e3smexp order by e3smexp.expid desc limit 1").fetchall()

        new_experiment = Exp(expid=currExpObj.expid,
                        user=timingProfileInfo['user'],
                        machine=timingProfileInfo['machine'],
                        exp_date=changeDateTime(timingProfileInfo['curr']),
                        upload_by = uploaduser,
                        exp_name=timingProfileInfo['case'],
                        total_pes_active=timingProfileInfo['total_pes'],
                        run_time=timingProfileInfo['run_time'],
                        mpi_tasks_per_node=timingProfileInfo['mpi_task'])
        db.session.add(new_experiment)
        #insert pelayout
        i=0
        while i < len(componentTable):
            new_pelayout = Pelayout(expid=currExpObj.expid,
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
            new_runtime = Runtime(expid=currExpObj.expid,
                        component=runTimeTable[i],
                        seconds=runTimeTable[i+1],
                        model_day=runTimeTable[i+2],
                        model_years=runTimeTable[i+3])
            db.session.add(new_runtime)
            i=i+4
        # Set return flag to True once all processing is complete.
        successFlag = True
        return (successFlag, duplicateFlag, currExpObj)
    except IndexError as e:
        print(('    ERROR: %s' %e))
        # Sarat: Rollback added to avoid auto-incrementing expid for failed uploads
        # Check if rollback doesn't cause issues with skipping incomplete exps
        db.session.rollback()
        return (successFlag, duplicateFlag, currExpObj) # skips this experiment
    except KeyError as e:
        print(('    ERROR: Missing data %s' %e))
        db.session.rollback()
        return (successFlag, duplicateFlag, currExpObj) # skips this experiment
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        print(('    SQL ERROR: %s' %e))
        db.session.rollback()
        return (successFlag, duplicateFlag, currExpObj) # skips this experiment
    except Exception as e:
        print(('    ERROR: %s' %e))
        print(('    Error encountered while parsing e3sm_timing file : %s' %convertPathtofile(filename)))
        db.session.rollback()
        return (successFlag, duplicateFlag, currExpObj) # skips this experiment

#needs here
# removes temporary folders in server
def removeFolder(removeroot,filename):
    # TODO: Validate filename before removing
    try:
        shutil.rmtree(os.path.join(removeroot,filename.split('.')[0]))
        os.remove(os.path.join(removeroot,filename))
    except OSError as e:
        print(("    Error: %s - %s." % (e.filename, e.strerror)))

    return

#need here
# aggregate files and store in file server
def zipFolder(exptag,exptaguser,exptagid,fpath):
    try:
        expname=0
        root=fpath
        for path, subdirs, files in os.walk(root):
            for name in subdirs:
                if name.startswith('CaseDocs.'+str(exptag)):
                    expname = 'exp-'+exptaguser+'-'+str(exptagid)
                    zipFileFullPath = os.path.join(EXP_DIR,expname)
                    shutil.make_archive(zipFileFullPath,'zip',path)
                    # upload files into file server
                    isSuccess=uploadMinio(EXP_DIR,expname)
                    if isSuccess == False:
                        return (False,zipFileFullPath)
    except IOError as e:
        print(('    ERROR: %s' %e))
        return (False,zipFileFullPath)
    return (True,zipFileFullPath)

#need here
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
    except InvalidResponseError as err:
        print(('    ERROR: Failed to upload to file server %s' %err))
        return (False)
    return True

#need here
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
                # If code crashes here, check if GPTL output file format has changed
                # Modify corresponding modelTiming.parse function
                utf8reader = codecs.getreader('utf-8')
                source = utf8reader(sourceFile.extractfile(element))
                new_modeltiming = ModelTiming(expid=expID, jsonVal=parseModelTiming.parse(source),rank=rankStr)
                db.session.add(new_modeltiming)
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        print(('    SQL ERROR: %s' %e))
        db.session.rollback()
        return (False) # skips this experiment
    except IndexError as e:
        print(('    ERROR: %s' %e))
        sourceFile.close()
        db.session.rollback()
        return (False) # skips this experiment
    except KeyError as e:
        print(('    ERROR: Missing data %s' %e))
        sourceFile.close()
        db.session.rollback()
        return (False) # skips this experiment
    except Exception as e:
        print(('[ERROR]: %s' % e))
        print(('    Error encountered while parsing model timing file %s' %convertPathtofile(mtFile)))
        db.session.rollback()
        sourceFile.close()
        return (False) # skips this experiment
    return

if __name__ == "__main__":
    if sys.argv[1]:
        filename = sys.argv[1]
    else:
        filename = '/Users/4g5/Downloads/exp-ac.golaz-73642'
    user = 'gaurabkcutk'
    parseData(filename,user)
