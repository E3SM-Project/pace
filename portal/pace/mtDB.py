#Author: Zachary Mitchell
#Purpose: A table that goes with e3sm_timing to bring nodes from the database.
from pace_common import *
from sqlalchemy import Table,Column,Integer,MetaData,create_engine,String,VARCHAR
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from subprocess import Popen,PIPE
import modelTiming as mt
import io

metadata = MetaData()
experimentsTable = Table('model_timing',metadata,\
Column('id',Integer,primary_key=True,autoincrement=True),\
Column('expID',Integer),\
Column('jsonVal',MEDIUMTEXT),\
Column('extension',VARCHAR(10)))

# Connection happens in common
dbConn, dbengine, dburl  = connectDatabase()
metadata.create_all(dbengine)
# dbConn = paceEngine.connect()

def insert(mtFile,expID):
    results = []
    dirList = Popen(["tar","--list","-f",mtFile],stdout=PIPE).communicate()[0].split("\n")
    for path in dirList:
        if len(path.split("/")) > 1 and "." in path.split("/")[1]:
            #This is a file we want! Let's save it:
            results.append({"expID":expID,"jsonVal":mt.parse(io.StringIO(u""+Popen(["tar","-xzf",mtFile,path,"-O"],stdout=PIPE).communicate()[0])),"extension":path.split("/")[1].split(".")[1]})
    dbConn.execute(experimentsTable.insert(),results)
    return
