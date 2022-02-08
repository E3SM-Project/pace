#! /usr/bin/env python3
# @file parse.py
# @brief initial flow process for parsing.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13
# imports
from pace.e3sm.e3smDb.datastructs import *
from . pace_common import *
db.create_all()
import sys


import tarfile
#from . import inputFileParser
from pace.e3sm.e3smParser import parseE3SM

PACE_LOG_DIR,EXP_DIR,UPLOAD_FOLDER = getDirectories()

# main
def parseData(zipfilename,uploaduser,project):
    # CHECKED: sanitize zipfilename and uploaduser (this is done in webapp.py at fileparse)
    # open file to write pace report
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    logfilename = 'pace-'+str(uploaduser)+'-'+str(datetime.now().strftime('%Y-%m-%d-%H:%M:%S'))+'.log'
    intlogfilename = "internal-" + logfilename
    logfilepath = PACE_LOG_DIR + logfilename
    intlogfilepath = PACE_LOG_DIR + intlogfilename
    log_file = open(logfilepath,'w')
    intlog_file = open(intlogfilepath,'w')
    sys.stdout = log_file
    sys.stderr = intlog_file
    print ("* * * * * * * * * * * * * * PACE Report * * * * * * * * * * * * * *")
    
    if project == 'e3sm':
        status = parseE3SM.parseData(zipfilename,uploaduser) #returns 'success' for successful integration
    else:
        print(" ")
        print("Invalid project %s" %project)
        status = 'fail'
    
    sys.stdout = old_stdout
    sys.stderr = old_stderr
    log_file.close()
    intlog_file.close()
    return(status+'/'+str(logfilename))

if __name__ == "__main__":
    if sys.argv[1]:
        filename = sys.argv[1]
    else:
        filename = '/Users/4g5/Downloads/exp-ac.golaz-73642'
    user = 'gaurabkcutk'
    parseData(filename,user)
