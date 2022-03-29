#! /usr/bin/env python3
# @file datastructs.py
# @brief PACE DB table class.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

from pace.__init__ import db
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

    def __init__(self,expid, user,machine,exp_date,upload_by,exp_name,total_pes_active,run_time,mpi_tasks_per_node):
        self.expid = expid
        self.user = user
        self.machine = machine
        self.exp_date = exp_date
        self.upload_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.upload_by = upload_by
        self.exp_name = exp_name
        self.total_pes_active = total_pes_active
        self.run_time = run_time
        self.mpi_tasks_per_node = mpi_tasks_per_node

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

    def __init__(self, case, lid, machine, caseroot, timeroot, user, exp_date,
                    long_res, res, compset, long_compset, stop_option, stop_n, run_length,
                    total_pes_active, mpi_tasks_per_node, pe_count_for_cost_estimate, model_cost, model_throughput, 
                    actual_ocn_init_wait_time, init_time, run_time, final_time, version, upload_by):
        self.case = case
        self.lid = lid
        self.machine = machine
        self.caseroot = caseroot
        self.timeroot = timeroot
        self.user = user
        self.exp_date = exp_date
        self.upload_date = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        self.long_res = long_res
        self.res = res
        self.compset = compset
        self.long_compset = long_compset
        self.stop_option = stop_option
        self.stop_n = stop_n
        self.run_length = run_length
        self.total_pes_active = total_pes_active
        self.mpi_tasks_per_node = mpi_tasks_per_node
        self.pe_count_for_cost_estimate = pe_count_for_cost_estimate
        self.model_cost = model_cost
        self.model_throughput = model_throughput
        self.actual_ocn_init_wait_time = actual_ocn_init_wait_time
        self.init_time = init_time
        self.run_time = run_time
        self.final_time = final_time
        self.version = version
        self.upload_by = upload_by

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

    def __init__(self, expid, component, comp_pes, root_pe, tasks, threads, instances, stride):
        self.expid = expid
        self.component = component
        self.comp_pes = comp_pes
        self.root_pe = root_pe
        self.tasks = tasks
        self.threads = threads
        self.instances = instances
        self.stride = stride

class Runtime(db.Model):
    __tablename__ = 'runtime'
    id = db.Column(INTEGER(unsigned=True), primary_key=True)
    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'), nullable=False, index=True)
    component = db.Column(db.String(25), nullable=False, index=True)
    seconds = db.Column(DECIMAL(10,3,unsigned=True), nullable=False)
    model_day = db.Column(DECIMAL(10,3,unsigned=True), nullable=False)
    model_years = db.Column(DECIMAL(10,2,unsigned=True), nullable=False)

    def __init__(self, expid,component,seconds,model_day,model_years):
        self.expid = expid
        self.component = component
        self.seconds = seconds
        self.model_day = model_day
        self.model_years = model_years
    

class ModelTiming(db.Model):
    __tablename__ = 'model_timing'
    id = db.Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'), nullable=False, index=True)
    jsonVal = db.Column(MEDIUMTEXT, nullable=False)
    rank = db.Column(db.String(10), nullable=False)

    def __init__(self,expid,jsonVal,rank):
        self.expid = expid
        self.jsonVal = jsonVal
        self.rank = rank

class Authusers(db.Model):
    id = db.Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    user = db.Column(db.String(50))

    def __init__(self,user):
        self.user = user

class Expnotes(db.Model):
    __tablename__ = 'expnotes'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, index=True)
    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'), nullable=False, index=True)
    note = db.Column(MEDIUMTEXT, nullable=False)

    def __init__(self,expid,note):
        self.expid = expid
        self.note = note

class useralias(db.Model):
    __tablename__ = 'useralias'
    id = db.Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    user = db.Column(db.String(25),nullable=False, index=True)
    alias = db.Column(db.String(25),nullable=False)

    def __init__(self, user, alias):
        self.user = user
        self.alias = alias
        

#new tables
class NamelistInputs(db.Model):
    __tablename__ = 'namelist_inputs'
    #id = Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'),
            nullable=False, index=True, primary_key=True)
    name = db.Column(db.VARCHAR(100), nullable=False, index=True, primary_key=True)
    data = db.Column(MEDIUMTEXT, nullable=False)

    def __init__(self, expid, name, data):
        self.expid = expid
        self.name = name
        self.data = data

class XMLInputs(db.Model):
    __tablename__ = 'xml_inputs'

    #id = Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'),
            nullable=False, index=True, primary_key=True)
    name = db.Column(db.VARCHAR(100), nullable=False, index=True, primary_key=True)
    data = db.Column(MEDIUMTEXT, nullable=False)

    def __init__(self, expid, name, data):
        self.expid = expid
        self.name = name
        self.data = data


class RCInputs(db.Model):
    __tablename__ = 'rc_inputs'

    #id = Column(INTEGER(unsigned=True), primary_key=True,autoincrement=True)
    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'),
            nullable=False, index=True, primary_key=True)
    name = db.Column(db.VARCHAR(100), nullable=False, index=True, primary_key=True)
    data = db.Column(MEDIUMTEXT, nullable=False)

    def __init__(self, expid, name, data):
        self.expid = expid
        self.name = name
        self.data = data

class ScorpioStats(db.Model):
    __tablename__ = 'scorpio_stats'

    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'),
            nullable=False, index=True, primary_key=True)
    name = db.Column(db.VARCHAR(100), nullable=False, index=True, primary_key=True)
    data = db.Column(MEDIUMTEXT, nullable=False)

    def __init__(self, expid, name, data):
        self.expid = expid
        self.name = name
        self.data = data

class BuildTime(db.Model):
    __tablename__ = 'build_time'

    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'),
            nullable=False, index=True, primary_key=True)
    data = db.Column(MEDIUMTEXT, nullable=False)

    def __init__(self, expid, data):
        self.expid = expid
        self.data = data


class MemfileInputs(db.Model):
    __tablename__ = 'memfile_inputs'

    expid = db.Column(INTEGER(unsigned=True), db.ForeignKey('e3smexp.expid'),
            nullable=False, index=True, primary_key=True)
    name = db.Column(db.VARCHAR(100), nullable=False, index=True, primary_key=True)
    data = db.Column(LONGTEXT, nullable=False)

    def __init__(self, expid, name, data):
        self.expid = expid
        self.name = name
        self.data = data

