#! /usr/bin/env python3
# @file parseCaseDocs.py
# @brief initial flow process for parsing files under CaseDocs folder.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import os, sys
from . datastructs import *
from pace.e3smParser import parseNameList
from pace.e3smParser import parseRC
from pace.e3smParser import parseXML

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

def loaddb_casedocs(casedocpath,db, expid):
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

                    nml = db.session.query(NamelistInputs).filter_by(expid=expid, name=name).first()
                    if nml:
                        print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

                    else:
                        nml = NamelistInputs(expid=expid, name=name, data=data)
                        db.session.add(nml)

                elif nameseq[0] in xmlfiles:
                    data = parseXML.loaddb_xmlfile(path)
                    
                    xml = db.session.query(XMLInputs).filter_by(expid=expid, name=name).first()

                    if xml:
                        print("Insertion is discarded due to dupulication: expid=%d, xml-name=%s" % (expid, name))

                    else:
                        xml = XMLInputs(expid=expid, name=name, data=data)
                        db.session.add(xml)

                elif nameseq[0] in rcfiles:
                    data = parseRC.loaddb_rcfile(path)
                    
                    rc = db.session.query(RCInputs).filter_by(expid=expid, name=name).first()

                    if rc:
                        print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

                    else:
                        rc = RCInputs(expid=expid, name=name, data=data)
                        db.session.add(rc)

                else:
                    pass
        else:
            pass
    return True

    
    