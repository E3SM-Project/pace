#! /usr/bin/env python
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

from datastructs import *
from flask_sqlalchemy import SQLAlchemy
import bson
from bson.objectid import ObjectId
# to get current username from env - used for uploadedBy
import getpass
from sqlalchemy import create_engine
import os
import stat
from stat import *
import getpass
import codecs
from ConfigParser import RawConfigParser
# SafeConfig parser does interpolation - refer to other desctions of file as %(foo)
# This causes problems with strings containing % - e.g., password
# from ConfigParser import SafeConfigParser
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Table,Column,Integer,MetaData,create_engine,String,VARCHAR
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

# Every file/tool will have a different last modified version in rep
# Hence parameterizing this to get lastVer (auto-expanded svn keyword Rev) as argument 
def getPACEVer(lastVer):
	# e.g., a = "$Rev : 54$" , a.strip('$').split(':')[1].strip() gives 54
	# PACE_VER = 'r' + lastVer.strip('$').split(':')[1].strip()
	# no 'r' prefix for ease of sorting by version number
	PACE_VER = 'r' + lastVer.strip('$').split(':')[1].strip()
	return PACE_VER

def readConfigFile(configFile):
	global PACE_USER
	filePerms = oct(os.stat(configFile)[ST_MODE])
	if filePerms != '0100600':
		print bcolors.WARNING + "Config file permissions should be set to read, write for owner only" 
		print "Please use chmod 600 " + configFile + " to dismiss this warning." + bcolors.ENDC
		# print filePerms

	parser = RawConfigParser()
	parser.read(configFile)
	myuser = parser.get('PACE','username')
	PACE_USER = myuser
	mypwd = parser.get('PACE','password')
	mydb = parser.get('PACE','db')
	myhost = parser.get('PACE','host')
	return myuser, mypwd, mydb, myhost

dbConn = ""
dbSession = ""
dbSessionf = ""
dbEngine = ""
dburl = ""
experimentsTable = ""

def initDatabase():	
	global dbConn, dbSession, dbSessionf, dbEngine, dburl, experimentsTable
	configFile = None
	if os.path.isfile('.pacerc'):
		configFile = '.pacerc'
	elif os.path.isfile(os.environ['HOME'] + '/.pacerc'):
		configFile = os.environ['HOME'] + '/.pacerc'
	elif os.path.isfile('/pace/prod/.pacerc') and os.access("/pace/prod/.pacerc", os.R_OK):
		configFile = '/pace/prod/.pacerc'
	elif os.path.isfile('/pace/dev1/.pacerc') and os.access("/pace/dev1/.pacerc", os.R_OK):
		configFile = '/pace/dev1/.pacerc'
	elif os.path.isfile('/pace/dev2/.pacerc') and os.access("/pace/dev2/.pacerc", os.R_OK):
		configFile = '/pace/dev2/.pacerc'
	elif os.path.isfile('/pace/dev3/.pacerc') and os.access("/pace/dev3/.pacerc", os.R_OK):
		configFile = '/pace/dev3/.pacerc'

	if configFile:
		print "Reading configuration from " + configFile 
		myuser,mypwd,mydb,myhost = readConfigFile(configFile)
	else:
		print bcolors.WARNING + "For convenience, you should create your configuration (.pacerc) using the template pacerc.tmpl"
		print "Alternately, you can enter your credentials below." + bcolors.ENDC
		myuser = raw_input('Username: ')
		mypwd = getpass.getpass()
		mydb = 'pace'
		myhost = 'localhost'

	dburl = 'mysql+pymysql://' + myuser + ':' + mypwd + '@' + myhost +  '/' + mydb

	dbEngine = create_engine(dburl, pool_recycle=3600)
	dbConn = dbEngine.connect()
	Base.metadata.create_all(dbEngine)
	Base.metadata.bind = dbConn
	dbSessionf = sessionmaker(bind=dbConn)
	dbSession = dbSessionf()

	metadata = MetaData()
	experimentsTable = Table('model_timing',metadata,\
	Column('id',Integer,primary_key=True,autoincrement=True),\
	Column('expID',Integer),\
	Column('jsonVal',MEDIUMTEXT),\
	Column('rank',VARCHAR(10)))

	metadata.create_all(dbEngine)
	return dbConn, dbEngine, dburl, dbSession

