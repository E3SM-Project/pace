from __init__ import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from datetime import datetime

class Timingprofile(db.Model):
	expid = db.Column(db.Integer, primary_key=True)    
	case = db.Column(db.String(100),nullable=False)
	lid = db.Column(db.String(50), nullable=False)
	machine = db.Column(db.String(25), nullable=False)
	caseroot = db.Column(db.String(250),nullable=False)	
	timeroot = db.Column(db.String(250),nullable=False)	
	user = db.Column(db.String(25),nullable=False)
	curr_date = db.Column(db.DateTime, default=datetime.utcnow)
	grid = db.Column(db.String(100),nullable=False)
	compset = db.Column(db.String(100),nullable=False)
	stop_option = db.Column(db.String(25),nullable=False)
	stop_n = db.Column(db.String(25),nullable=False)        
	run_length = db.Column(db.Integer, nullable=False)
	total_pes_active = db.Column(db.Integer, nullable=False)
	mpi_tasks_per_node = db.Column(db.Integer, nullable=False)
	pe_count_for_cost_estimate = db.Column(db.Integer, nullable=False)
	model_cost = db.Column(db.String(50), nullable=False)
	model_throughput = db.Column(db.Float, nullable=False)
	actual_ocn_init_wait_time = db.Column(db.String(25), nullable=False)

class Pelayout(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	expid = db.Column(db.Integer, nullable=False)
	component = db.Column(db.String(25), nullable=False)
	comp_pes = db.Column(db.Integer, nullable=False)
	root_pe = db.Column(db.Integer, nullable=False)
	tasks = db.Column(db.Integer, nullable=False)
	threads = db.Column(db.String(10), nullable=False)
	instances = db.Column(db.Integer, nullable=False)
	stride = db.Column(db.Integer, nullable=False)

class Runtime(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	expid = db.Column(db.Integer, nullable=False)
	component = db.Column(db.String(25), nullable=False)
	seconds = db.Column(db.Float, nullable=False)
	model_day = db.Column(db.Float, nullable=False)
	model_years = db.Column(db.Float, nullable=False)
	

class ModelTiming(db.Model):
	id = db.Column(db.Integer, primary_key=True,autoincrement=True)
	expid = db.Column(db.Integer, nullable=False)
	jsonVal = db.Column(MEDIUMTEXT, nullable=False)
	rank = db.Column(db.String(10), nullable=False)
