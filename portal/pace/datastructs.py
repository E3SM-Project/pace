from __init__ import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import MEDIUMTEXT,INTEGER,DECIMAL
from datetime import datetime

class Timingprofile(db.Model):
	expid = db.Column(INTEGER(unsigned=True), primary_key=True, index=True)     
	case = db.Column(db.String(100),nullable=False, index=True)
	lid = db.Column(db.String(50), nullable=False)
	machine = db.Column(db.String(25), nullable=False, index=True)
	caseroot = db.Column(db.String(250),nullable=False)	
	timeroot = db.Column(db.String(250),nullable=False)	
	user = db.Column(db.String(25),nullable=False, index=True)
	exp_date = db.Column(db.DateTime,nullable=False)
	upload_date = db.Column(db.DateTime,default=datetime.utcnow)
	long_res = db.Column(db.String(100),nullable=False)
	res = db.Column(db.String(50),nullable=False)
	compset = db.Column(db.String(50),nullable=False, index=True)
	long_compset = db.Column(db.String(100),nullable=False)
	stop_option = db.Column(db.String(25),nullable=False)
	stop_n = db.Column(INTEGER(unsigned=True),nullable=False)        
	run_length = db.Column(INTEGER(unsigned=True), nullable=False)
	total_pes_active = db.Column(INTEGER(unsigned=True), nullable=False)
	mpi_tasks_per_node = db.Column(INTEGER(unsigned=True), nullable=False)
	pe_count_for_cost_estimate = db.Column(INTEGER(unsigned=True), nullable=False)
	model_cost = db.Column(DECIMAL(20,2,unsigned=True), nullable=False)
	model_throughput = db.Column(DECIMAL(10,2,unsigned=True), nullable=False)
	actual_ocn_init_wait_time = db.Column(DECIMAL(10,3,unsigned=True), nullable=False)
	init_time = db.Column(DECIMAL(10,3,unsigned=True), nullable=False)
	run_time = db.Column(DECIMAL(20,3,unsigned=True), nullable=False)
	final_time = db.Column(DECIMAL(10,3,unsigned=True), nullable=False)
	version = db.Column(db.String(100),nullable=False)
	

class Pelayout(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('timingprofile.expid'), nullable=False, index=True)
	component = db.Column(db.String(25), nullable=False, index=True)
	comp_pes = db.Column(INTEGER(unsigned=True), nullable=False)
	root_pe = db.Column(INTEGER(unsigned=True), nullable=False)
	tasks = db.Column(INTEGER(unsigned=True), nullable=False)
	threads = db.Column(INTEGER(unsigned=True), nullable=False)
	instances = db.Column(INTEGER(unsigned=True), nullable=False)
	stride = db.Column(INTEGER(unsigned=True), nullable=False)

class Runtime(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True)
	expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('timingprofile.expid'), nullable=False, index=True)
	component = db.Column(db.String(25), nullable=False, index=True)
	seconds = db.Column(DECIMAL(10,3,unsigned=True), nullable=False)
	model_day = db.Column(DECIMAL(10,3,unsigned=True), nullable=False)
	model_years = db.Column(DECIMAL(10,2,unsigned=True), nullable=False)
	

class ModelTiming(db.Model):
	id = db.Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
	expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('timingprofile.expid'), nullable=False, index=True)
	jsonVal = db.Column(MEDIUMTEXT, nullable=False)
	rank = db.Column(db.String(10), nullable=False)
