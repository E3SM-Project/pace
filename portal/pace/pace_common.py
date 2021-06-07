#! /usr/bin/env python3
# @file pace_common.py
# @brief: Common helper functions for PACE
#
import os
import string
import sys
import argparse
from datetime import datetime
from sqlalchemy import Table,Column,Integer,MetaData,create_engine,String,VARCHAR
from sqlalchemy.dialects.mysql import MEDIUMTEXT

# Avoid circular imports - so, don't import datastructs here
#from datastructs import *

from flask_sqlalchemy import SQLAlchemy
# to get current username from env - used for uploadedBy
import getpass
from sqlalchemy import create_engine
import os
import stat
from stat import *
import getpass
import codecs
#from ConfigParser import RawConfigParser
from configparser import RawConfigParser
# SafeConfig parser does interpolation - refer to other desctions of file as %(foo)
# This causes problems with strings containing % - e.g., password
# from ConfigParser import SafeConfigParser

from sqlalchemy.dialects.mysql import MEDIUMTEXT

# Global var
PACE_USER = 'yourusername'
LAST_MODIFIED_VER = "$Rev$"
PACE_VER = ''

### Helper functions etc... ####
# Colors for console text
class bcolors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    RED = '\033[31m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    CYAN = '\033[36m'

def getPACEUser():
    return PACE_USER

def getDirectories():
    # PACE Report directory PACE_LOG_DIR
    # Raw data directory EXP_DIR
    # upload directory UPLOAD_FOLDER
    if os.getenv("PACE_DOCKER_INSTANCE"):
        return "/pace/portal/pace/static/logs/","/pace/portal/pace/static/data/","/pace/portal/upload/"
    return '/pace/assets/static/logs/','/pace/assets/static/data/','/pace/prod/portal/upload'

# Every file/tool will have a different last modified version in rep
# Hence parameterizing this to get lastVer (auto-expanded svn keyword Rev) as argument
def getPACEVer(lastVer):
    # e.g., a = "$Rev : 54$" , a.strip('$').split(':')[1].strip() gives 54
    # PACE_VER = 'r' + lastVer.strip('$').split(':')[1].strip()
    # no 'r' prefix for ease of sorting by version number
    PACE_VER = 'r' + lastVer.strip('$').split(':')[1].strip()
    return PACE_VER

#Grab the appropriate Pace RC file. It will be different depending on who (or what) is running this script:
def detectPaceRc():
    configFile = None
    locations=["prod","dev1","dev2","dev3"]
    if os.path.isfile('.pacerc'):
        configFile = '.pacerc'
    elif os.getenv("PACE_DOCKER_INSTANCE"):
        configFile="/pace/docker/rc/.pacerc"
    else:
        for item in locations:
            if os.path.isfile('/pace/'+item+'/.pacerc') and os.access('/pace/'+item+'/.pacerc', os.R_OK):
                configFile = '/pace/'+item+"/.pacerc"
                break
    return configFile

def getMiniokey():
    configFile = detectPaceRc()
    myAkey = None
    mySkey = None
    myMiniourl = None

    filePerms = oct(os.stat(configFile)[ST_MODE])
    if filePerms not in ['0100600','0o100600']:
        print((bcolors.WARNING + "Config file permissions should be set to read, write for owner only"))
        print(("Please use chmod 600 " + configFile + " to dismiss this warning." + bcolors.ENDC))
    # print filePerms
    parser = RawConfigParser()
    parser.read(configFile)
    myAkey = parser.get('MINIO','minio_access_key')
    mySkey = parser.get('MINIO','minio_secret_key')
    myMiniourl = parser.get('MINIO','minio_url')

    return myAkey, mySkey, myMiniourl

def getGithubkey():
    configFile = detectPaceRc()
    myClientid = None
    myClientsecret = None

    filePerms = oct(os.stat(configFile)[ST_MODE])
    if filePerms not in ['0100600','0o100600']:
        print((bcolors.WARNING + "Config file permissions should be set to read, write for owner only"))
        print(("Please use chmod 600 " + configFile + " to dismiss this warning." + bcolors.ENDC))
    # print filePerms
    parser = RawConfigParser()
    parser.read(configFile)
    myClientid = parser.get('GITHUBAPP','githubapp_client_id')
    myClientsecret = parser.get('GITHUBAPP','githubapp_secret_key')

    return myClientid, myClientsecret

def readConfigFile(configFile):
    global PACE_USER
    filePerms = oct(os.stat(configFile)[ST_MODE])
    if filePerms not in ['0100600','0o100600']:
        print((bcolors.WARNING + "Config file permissions should be set to read, write for owner only"))
        print(("Please use chmod 600 " + configFile + " to dismiss this warning." + bcolors.ENDC))
        # print filePerms

    parser = RawConfigParser()
    parser.read(configFile)
    myuser = parser.get('PACE','username')
    PACE_USER = myuser
    mypwd = parser.get('PACE','password')
    mydb = parser.get('PACE','db')
    myhost = parser.get('PACE','host')
    return myuser, mypwd, mydb, myhost


dburl = ""

def initDatabase():
    global dburl
    configFile = detectPaceRc()

    if configFile:
        print(("Reading configuration from " + configFile))
        myuser,mypwd,mydb,myhost = readConfigFile(configFile)
    else:
        print((bcolors.WARNING + "For convenience, you should create your configuration (.pacerc) using the template pacerc.tmpl"))
        print(("Alternately, you can enter your credentials below." + bcolors.ENDC))
        myuser = input('Username: ')
        mypwd = getpass.getpass()
        mydb = 'pace'
        myhost = 'localhost'

    dburl = 'mysql+pymysql://' + myuser + ':' + mypwd + '@' + myhost +  '/' + mydb

    # Ref: https://docs.sqlalchemy.org/en/latest/core/pooling.html
    return dburl
