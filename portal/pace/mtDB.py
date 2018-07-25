#Author: Zachary Mitchell
#Purpose: A table that goes with e3sm_timing to bring nodes from the database.
from sqlalchemy import Table,Column,Integer,MetaData
from sqlalchemy.dialects.mysql import MEDIUMTEXT

metadata = MetaData
experimentsTable = Table('experiments',metadata,\
Column('id',Integer,primary_key=True,autoincrement=True),\
Column('expID',Integer),\
Column('jsonVal',MEDIUMTEXT))