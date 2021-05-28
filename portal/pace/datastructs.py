from . __init__ import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.mysql import MEDIUMTEXT,INTEGER,DECIMAL
from datetime import datetime

class Exp(db.Model):
    __tablename__ = 'exp'
    expid = db.Column(INTEGER(unsigned=True), primary_key=True, index=True) 
    user = db.Column(db.String(25),nullable=False, index=True)
    machine = db.Column(db.String(25), nullable=False, index=True)
    exp_date = db.Column(db.DateTime,nullable=False)
    upload_date = db.Column(db.DateTime,default=datetime.utcnow)
    upload_by = db.Column(db.String(25),nullable=False, default='sarat')
    exp_name = db.Column(db.String(200),nullable=False, index=True)
    total_pes_active = db.Column(INTEGER(unsigned=True), nullable=False)
    run_time = db.Column(DECIMAL(20,3,unsigned=True), nullable=False)
    mpi_tasks_per_node = db.Column(INTEGER(unsigned=True), nullable=False)

class E3SMexp(db.Model):
    __tablename__ = 'e3smexp'
    expid = db.Column(INTEGER(unsigned=True), primary_key=True, index=True)     
    case = db.Column(db.String(200),nullable=False, index=True)
    lid = db.Column(db.String(50), nullable=False)
    machine = db.Column(db.String(25), nullable=False, index=True)
    caseroot = db.Column(db.String(250),nullable=False)    
    timeroot = db.Column(db.String(250),nullable=False)    
    user = db.Column(db.String(25),nullable=False, index=True)
    exp_date = db.Column(db.DateTime,nullable=False)
    upload_date = db.Column(db.DateTime,default=datetime.utcnow)
    long_res = db.Column(db.String(200),nullable=False)
    res = db.Column(db.String(100),nullable=False)
    compset = db.Column(db.String(100),nullable=False, index=True)
    long_compset = db.Column(db.String(200),nullable=False)
    stop_option = db.Column(db.String(25),nullable=False)
    stop_n = db.Column(INTEGER(unsigned=True),nullable=False)        
    run_length = db.Column(INTEGER(unsigned=True), nullable=False)
    total_pes_active = db.Column(INTEGER(unsigned=True), nullable=False)
    mpi_tasks_per_node = db.Column(INTEGER(unsigned=True), nullable=False)
    pe_count_for_cost_estimate = db.Column(INTEGER(unsigned=True), nullable=False)
    model_cost = db.Column(DECIMAL(20,2,unsigned=True), nullable=False)
    model_throughput = db.Column(DECIMAL(20,2,unsigned=True), nullable=False)
    actual_ocn_init_wait_time = db.Column(DECIMAL(10,3,unsigned=True), nullable=False)
    init_time = db.Column(DECIMAL(10,3,unsigned=True), nullable=False)
    run_time = db.Column(DECIMAL(20,3,unsigned=True), nullable=False)
    final_time = db.Column(DECIMAL(10,3,unsigned=True), nullable=False)
    version = db.Column(db.String(100),nullable=False)
    upload_by = db.Column(db.String(25),nullable=False, default='sarat')

class Pelayout(db.Model):
    __tablename__ = 'pelayout'
    id = db.Column(INTEGER(unsigned=True), primary_key=True)
    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'), nullable=False, index=True)
    component = db.Column(db.String(25), nullable=False, index=True)
    comp_pes = db.Column(INTEGER(unsigned=True), nullable=False)
    root_pe = db.Column(INTEGER(unsigned=True), nullable=False)
    tasks = db.Column(INTEGER(unsigned=True), nullable=False)
    threads = db.Column(INTEGER(unsigned=True), nullable=False)
    instances = db.Column(INTEGER(unsigned=True), nullable=False)
    stride = db.Column(INTEGER(unsigned=True), nullable=False)

class Runtime(db.Model):
    __tablename__ = 'runtime'
    id = db.Column(INTEGER(unsigned=True), primary_key=True)
    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'), nullable=False, index=True)
    component = db.Column(db.String(25), nullable=False, index=True)
    seconds = db.Column(DECIMAL(10,3,unsigned=True), nullable=False)
    model_day = db.Column(DECIMAL(10,3,unsigned=True), nullable=False)
    model_years = db.Column(DECIMAL(10,2,unsigned=True), nullable=False)
    

class ModelTiming(db.Model):
    __tablename__ = 'model_timing'
    id = db.Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'), nullable=False, index=True)
    jsonVal = db.Column(MEDIUMTEXT, nullable=False)
    rank = db.Column(db.String(10), nullable=False)

class Authusers(db.Model):
    id = db.Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    user = db.Column(db.String(50))

class Expnotes(db.Model):
    __tablename__ = 'expnotes'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, index=True)
    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'), nullable=False, index=True)
    note = db.Column(MEDIUMTEXT, nullable=False)

class useralias(db.Model):
    __tablename__ = 'useralias'
    id = db.Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    user = db.Column(db.String(25),nullable=False, index=True)
    alias = db.Column(db.String(25),nullable=False)
