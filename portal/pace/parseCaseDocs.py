import os, sys
from . datastructs import *
from . import parseCaseDocsNameList
from . import parseCaseDocsRC
from . import parseCaseDocsXML

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
                    data = parseCaseDocsNameList.loaddb_namelist(path)
                    
                    nml = db.session.query(NamelistInputs).filter_by(expid=expid, name=name).first()
                    if nml:
                        print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

                    else:
                        nml = NamelistInputs(expid=expid, name=name, data=data)
                        db.session.add(nml)

                elif nameseq[0] in xmlfiles:
                    data = parseCaseDocsXML.loaddb_xmlfile(path)

                    xml = db.session.query(XMLInputs).filter_by(expid=expid, name=name).first()

                    if xml:
                        print("Insertion is discarded due to dupulication: expid=%d, xml-name=%s" % (expid, name))

                    else:
                        xml = XMLInputs(expid=expid, name=name, data=data)
                        db.session.add(xml)

                elif nameseq[0] in rcfiles:
                    data = parseCaseDocsRC.loaddb_rcfile(path)

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


if __name__ == "__main__":
    # "e3sm_timing." file list
    allfile=[]
    # "timing." file list
    timingfile=[]
    # "README.case." file list
    readmefile=[]
    # "GIT_DESCRIBE." file list
    gitdescribefile=[]
    #scorpio file
    scorpiofile = []
    #memory file
    memoryfile =[]
    # CaseDocs
    casedocs = []
    root=os.path.join(sys.argv[1])
    for path, subdirs, files in os.walk(root):
        for name in files:
            if name.startswith("timing."):
                timingfile.append(os.path.join(path, name))
            elif name.startswith("e3sm_timing."):
                allfile.append(os.path.join(path, name))
            elif name.startswith("README.case."):
                readmefile.append(os.path.join(path, name))
            elif name.startswith("GIT_DESCRIBE."):
                gitdescribefile.append(os.path.join(path, name))
            elif name.startswith("spio_stats."):
                scorpiofile.append(os.path.join(path, name))
            elif name.startswith("memory."):
                memoryfile.append(os.path.join(path, name))
        for name in subdirs:
            if name.startswith("CaseDocs."):
                casedocs.append(os.path.join(path, name))
    
    print(casedocs)
    #print(convertPathtofile(casedocs[0]))

    for case in casedocs:
        loaddb_casedocs(case,0,0)
    
    