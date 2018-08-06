from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, ForeignKey, Integer, String, TEXT
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Table,Column,Integer,MetaData,create_engine,String,VARCHAR
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from pace_common import *

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
	

class ModelTiming(Base):
	__tablename__ = 'model_timing'
	id = Column(Integer, primary_key=True,autoincrement=True)
	expid=Column(Integer, nullable=False)
	jsonVal=Column(MEDIUMTEXT, nullable=False)
	rank=Column(String(10), nullable=False)


