#! /usr/bin/env python3
# @file parseCaseDocs.py
# @brief initial flow process for parsing files under CaseDocs folder.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import os, sys, json
from pace.e3sm.e3smDb.datastructs import *
from pace.e3sm.e3smParser import parseNameList
from pace.e3sm.e3smParser import parseRC
from pace.e3sm.e3smParser import parseXML

#acceptable file name prefix
namelists = ("atm_in", "atm_modelio", "cpl_modelio", "drv_flds_in", "drv_in",
             "esp_modelio", "glc_modelio", "ice_modelio", "lnd_in",
             "lnd_modelio", "mosart_in", "mpaso_in", "mpassi_in",
             "ocn_modelio", "rof_modelio", "user_nl_cam", "user_nl_clm",
             "user_nl_cpl", "user_nl_mosart", "user_nl_mpascice",
             "user_nl_mpaso", "wav_modelio", "iac_modelio", "docn_in",
             "user_nl_docn", "user_nl_cice", "ice_in", "user_nl_elm",
             "user_nl_eam")

xmlfiles = ("env_archive", "env_batch", "env_build", "env_case",
            "env_mach_pes", "env_mach_specific", "env_run", "env_workflow",
            )

rcfiles = ("seq_maps",)


memfiles = ("memory",)

spiofiles = ("spio_stats",)

exclude_zipfiles = []
excludes_casedocs = ["env_mach_specific.xml~"]
excludes_gzfiles = []


def getCaseGroup(jsondata):
    caseDir = jsondata["file"]["group"]
    try:
        for model in caseDir:
            if '@id' in model and model['@id']=='case_desc' and 'entry' in model:
                for entry in model['entry']:
                    if '@id' in entry and entry['@id']=='CASE_GROUP':
                        if '@value' in entry:
                            return entry['@value']
                        else:
                            return None
    except Exception as e:
        print('Error while getting case_group')
        print(e)
        return None

def getEnvBuild(jsondata):
    output = {
        'compiler':None,
        'mpilib':None
    }
    buildModel = jsondata["file"]["group"]

    try:
        for model in buildModel:
            if '@id' in model and model['@id']=='build_macros' and 'entry' in model:
                for entry in model['entry']:
                    if '@id' in entry and entry['@id']=='COMPILER':
                        if '@value' in entry:
                            output['compiler'] = entry['@value']
                    elif '@id' in entry and entry['@id'] == 'MPILIB':
                        if '@value' in entry:
                            output['mpilib'] = entry['@value']
        return output
    except Exception as e:
        print('Error while getting build_macros information')
        print(e)
        return output


'''
    This function goes through casedocs folder in e3sm experiment and parses certain files by calling 
    its respective parser.
'''
def loaddb_casedocs(casedocpath,db, currExpObj):
    expid = currExpObj.expid
    for item in os.listdir(casedocpath):
        basename, ext = os.path.splitext(item)
        path = os.path.join(casedocpath, item)
        if any(basename.startswith(e) for e in excludes_casedocs):
            continue

        if os.path.isfile(path) and ext == ".gz":
            #prefix, _ = basename.split(".", 1)
            nameseq = []
            for n in basename.split("."):
                if n.isdigit():
                    break
                nameseq.append(n)
            name = ".".join(nameseq)
            if nameseq:
                if nameseq[0] in namelists:
                    data = parseNameList.loaddb_namelist(path)
                    if not data:
                        continue
                    nml = db.session.query(NamelistInputs).filter_by(expid=expid, name=name).first()
                    if nml:
                        print("Insertion is discarded due to duplication: expid=%d, name=%s" % (expid, name))

                    else:
                        nml = NamelistInputs(expid=expid, name=name, data=data)
                        db.session.add(nml)

                elif nameseq[0] in xmlfiles:
                    data = parseXML.loaddb_xmlfile(path)
                    if not data:
                        continue
                    if nameseq[0] == 'env_case':
                        case_group = getCaseGroup(json.loads(data))
                        currExpObj.case_group = case_group
                        db.session.merge(currExpObj)
                    elif nameseq[0] == 'env_build':
                        envBuildData = getEnvBuild(json.loads(data))
                        currExpObj.compiler = envBuildData['compiler']
                        currExpObj.mpilib = envBuildData['mpilib']
                        db.session.merge(currExpObj)
                    xml = db.session.query(XMLInputs).filter_by(expid=expid, name=name).first()

                    if xml:
                        print("Insertion is discarded due to duplication: expid=%d, xml-name=%s" % (expid, name))

                    else:
                        xml = XMLInputs(expid=expid, name=name, data=data)
                        db.session.add(xml)

                elif nameseq[0] in rcfiles:
                    data = parseRC.loaddb_rcfile(path)
                    if not data:
                        continue
                    rc = db.session.query(RCInputs).filter_by(expid=expid, name=name).first()

                    if rc:
                        print("Insertion is discarded due to duplication: expid=%d, name=%s" % (expid, name))

                    else:
                        rc = RCInputs(expid=expid, name=name, data=data)
                        db.session.add(rc)

                else:
                    pass
        else:
            pass
    return True

    
    