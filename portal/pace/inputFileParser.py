import sys, os
#from . datastructs import *
from tempfile import TemporaryDirectory
from zipfile import ZipFile


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

#makefiles = ("Depends.intel",)
makefiles = ("Depends",)

memfiles = ("memory",)

spiofiles = ("spio_stats",)

exclude_zipfiles = []
excludes_casedocs = ["env_mach_specific.xml~"]
excludes_gzfiles = []


def loaddb_spiofile(expid, name, spiofile):

    # TODO: handle a direcotry generated from this gz file
    # TODO: select a json file

    sptar = tarfile.open(spiofile, "r:gz")
    
    jsonmember = None
    jsondata = None

    for member in sptar.getmembers():
        if member.isfile() and member.name.endswith("json"):
            if jsonmember is None or jsonmember.size < member.size:
                jsonmember = member

    if jsonmember:
        jsondata = sptar.extractfile(jsonmember).read()

    sptar.close()

    #cmd = ["gunzip", spiofile]
    #mgr = self.get_manager()
    #ret, fwds = mgr.run_command(cmd)

    #spioitems = []

    #for item in fwds["data"]:
    #    spioitems.append(item.to_source())

    #jsondata = json.dumps(memitems)

    spio = self.session.query(SpiofileInputs).filter_by(
            expid=expid, name=name).first()

    if self.verify_db:
        if not spio or jsondata != spio.data:
            print("#######################################################")
            print("spiofile verification failure: expid=%d, name=%s" % (expid, name))
            print("From e3sm experiment:")
            print(jsondata)
            print("-------------------------------------------------------")
            print("From database:")
            print(spio.data if spio else spio)
    else:
        if spio:
            print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

        elif jsondata is None:
            print("Json data read error: expid=%d, name=%s" % (expid, name))

        else:
            spio = SpiofileInputs(expid, name, jsondata)
            self.session.add(spio)

def loaddb_memfile(expid, name, memfile):

    cmd = ["gunzip", memfile]

    mgr = self.get_manager()
    ret, fwds = mgr.run_command(cmd)

    memitems = []

    for item in fwds["data"]:
        memitems.append(item.to_source())

    # TODO: json load?
    jsondata = json.dumps(memitems)

    #try:
    mem = self.session.query(MemfileInputs).filter_by(
            expid=expid, name=name).first()

    if self.verify_db:
        if not mem or jsondata != mem.data:
            print("#######################################################")
            print("memfile verification failure: expid=%d, name=%s" % (expid, name))
            print("From e3sm experiment:")
            print(jsondata)
            print("-------------------------------------------------------")
            print("From database:")
            print(mem.data if mem else mem)
    else:
        if mem:
            print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

        else:
            mem = MemfileInputs(expid, name, jsondata)
            self.session.add(mem)

def loaddb_makefile(expid, name, makefile):

    cmd = ["gunzip", makefile, "--", "parsemk",  "@data"]

    mgr = self.get_manager()
    ret, fwds = mgr.run_command(cmd)

    mkitems = []

    for item in fwds["data"]:
        mkitems.append(item.to_source())

    jsondata = json.dumps(mkitems)

    #try:
    mk = self.session.query(MakefileInputs).filter_by(
            expid=expid, name=name).first()

    if self.verify_db:
        if not mk or jsondata != mk.data:
            print("#######################################################")
            print("makefile verification failure: expid=%d, name=%s" % (expid, name))
            print("From e3sm experiment:")
            print(jsondata)
            print("-------------------------------------------------------")
            print("From database:")
            print(mk.data if mk else mk)
    else:
        if mk:
            print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

        else:
            mk = MakefileInputs(expid, name, jsondata)
            self.session.add(mk)

    #except (InvalidRequestError, IntegrityError) as err:
    #    print("Missing expid in database: expid=%d, makefile-name=%s" % (expid, name))


def loaddb_rcfile(expid, name, rcpath):

    cmd = ["gunzip", rcpath]
    mgr = self.get_manager()
    ret, fwds = mgr.run_command(cmd)

    rcitems = []

    for line in fwds["data"].strip().split("\n"):
        items = tuple(l.strip() for l in line.split(":"))

        if len(items)==2:
            rcitems.append('"%s":%s' % items)

    jsondata = "{%s}" % ",".join(rcitems) 

    #try:
    rc = self.session.query(RCInputs).filter_by(
            expid=expid, name=name).first()

    if self.verify_db:
        #e3smdump = json.dumps(rc.data, sort_keys=True) if rc else ""
        #dbdump = json.dumps(jsondata, sort_keys=True)
        #if e3smdump != dbdump:
        if not rc or jsondata != rc.data:
            print("#######################################################")
            print("rc verification failure: expid=%d, name=%s" % (expid, name))
            print("From e3sm experiment:")
            #print(e3smdump)
            print(jsondata)
            print("-------------------------------------------------------")
            print("From database:")
            #print(dbdump)
            print(rc.data if rc else rc)
    else:
        if rc:
            print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

        else:
            rc = RCInputs(expid, name, jsondata)
            self.session.add(rc)

    #except (InvalidRequestError, IntegrityError) as err:
    #    print("Missing expid in database: expid=%d, rc-name=%s" % (expid, name))

def loaddb_xmlfile(expid, name, xmlpath):

    cmd = ["gunzip", xmlpath, "--", "uxml2dict",  "@data", "--",
            "dict2json", "@data"]

    from xml.parsers.expat import ExpatError

    try:
        mgr = self.get_manager()
        ret, fwds = mgr.run_command(cmd)

        jsondata = fwds["data"]

        xml = self.session.query(XMLInputs).filter_by(
                expid=expid, name=name).first()

        if self.verify_db:
            #e3smdump = json.dumps(xml.data, sort_keys=True) if xml else ""
            #dbdump = json.dumps(jsondata, sort_keys=True)
            #if e3smdump != dbdump:
            if not xml or jsondata != xml.data:
                print("#######################################################")
                print("xml verification failure: expid=%d, name=%s" % (expid, name))
                print("From e3sm experiment:")
                #print(e3smdump)
                print(jsondata)
                print("-------------------------------------------------------")
                print("From database:")
                #print(dbdump)
                print(xml.data if xml else xml)
        else:
            if xml:
                print("Insertion is discarded due to dupulication: expid=%d, xml-name=%s" % (expid, name))

            else:
                xml = XMLInputs(expid, name, jsondata)
                self.session.add(xml)

    except ExpatError as err:
        print("Warning: %s" % str(err))

    #except (InvalidRequestError, IntegrityError) as err:
    #    print("Missing expid in database: expid=%d, xml-name=%s" % (expid, name))

    #except Exception as err:
    #    print("Warning: %s" % str(err))
    #    import pdb; pdb.set_trace()
    #    print(err)

def loaddb_namelist(expid, name, nmlpath):

    cmd = ["gunzip", nmlpath, "--", "nmlread",  "@data", "--",
                "dict2json", "@data"]

    jsondata = None

    try:
        mgr = self.get_manager()
        ret, fwds = mgr.run_command(cmd)

        jsondata = fwds["data"]

    except IndexError as err:
        if name.startswith("user_nl"):
            jsondata = ""

        else:
            import pdb; pdb.set_trace()
            raise err
            
    except StopIteration as err:
        print("Warning: %s" % str(err))

    except Exception as err:
        print("Warning: %s" % str(err))
        import pdb; pdb.set_trace()
        print(err)

    #try:
    nml = self.session.query(NamelistInputs).filter_by(
                expid=expid, name=name).first()

    if self.verify_db:
        #e3smdump = json.dumps(nml.data, sort_keys=True) if nml else ""
        #dbdump = json.dumps(jsondata, sort_keys=True)
        #if e3smdump != dbdump:
        if not nml or jsondata != nml.data:
            print("#######################################################")
            print("namelist verification failure: expid=%d, name=%s" % (expid, name))
            print("From e3sm experiment:")
            #print(e3smdump)
            print(jsondata)
            print("-------------------------------------------------------")
            print("From database:")
            #print(dbdump)
            print(nml.data if nml else nml)

    elif jsondata:
        if nml:
            print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

        else:
            nml = NamelistInputs(expid, name, jsondata)
            self.session.add(nml)

    #except (InvalidRequestError, IntegrityError) as err:
    #    print("Missing expid in database: expid=%d, namelist-name=%s" % (expid, name))

def loaddb_casedocs(expid, casedocpath):

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

            if nameseq[0] in namelists:
                self.loaddb_namelist(expid, name, path)

            elif nameseq[0] in xmlfiles:
                self.loaddb_xmlfile(expid, name, path)

            elif nameseq[0] in rcfiles:
                self.loaddb_rcfile(expid, name, path)

            elif nameseq[0] in makefiles:
                self.loaddb_makefile(expid, name, path)

            elif nameseq[0] in memfiles:
                self.loaddb_memfile(expid, name, path)

#                elif any(basename.startswith(p) for p in makefiles):
#                    for makefile in makefiles:
#                        if basename.startswith(makefile):
#                            self.loaddb_makefile(expid, makefile, path)
#                            break
            else:
                pass
                #print("Warning: %s is not parsed." % basename)

        else:
            pass

def loaddb_e3smexp(zippath,db,expid):

    head, tail = os.path.split(zippath)
    basename, ext = os.path.splitext(tail)
    items = basename.split("-")
    print("-------items---------")
    print(items)
    if ext == ".zip" and len(items)==3:
        #expid = int(items[2])

        

        with ZipFile(zippath) as myzip:

            unzipdir = os.path.join(tempdir, basename)
            myzip.extractall(path=unzipdir)

            try:
                for item in os.listdir(unzipdir):
                    if item.startswith(".") or item in exclude_zipfiles:
                        continue

                    basename, ext = os.path.splitext(item)
                    path = os.path.join(unzipdir, item)

                    if os.path.isdir(path):

                        if basename.startswith("CaseDocs"):
                            loaddb_casedocs(expid, path)

                        else:
                            pass

                    elif os.path.isfile(path) and ext == ".gz":

                        if any(basename.startswith(e) for e in excludes_gzfiles):
                            continue

                        nameseq = []
                        for n in basename.split("."):
                            if n.isdigit():
                                break
                            nameseq.append(n)
                        name = ".".join(nameseq)

                        if nameseq[0] in spiofiles:
                            self.loaddb_spiofile(expid, name, path)

                        else:
                            pass
                    else:
                        pass

                if not self.verify_db:

                        if self.commit_updates:
                            self.session.commit()

                        else:
                            print("INFO: pacedb ended without committing any "
                                    "staged database transaction.")

            except (InvalidRequestError, IntegrityError) as err:
                print("Warning: database integrity error at %s: %s" % (zippath, str(err)))
                self.session.rollback()

            finally:                
                shutil.rmtree(unzipdir, ignore_errors=True)

def perform(args):

    self.show_progress = args.progress
    self.verify_db = args.verify
    self.create_expid_table = args.create_expid_table
    self.commit_updates = args.commit

    for datapath in args.datapath:
        inputpath = datapath["_"]

        if not args.db_session:
            dbcfg = args.db_cfg["_"]
            if not os.path.isfile(dbcfg):
                print("Could not find database configuration file: %s" % dbcfg)
                sys.exit(-1)

            with open(dbcfg) as f:
                myuser, mypwd, myhost, mydb = f.read().strip().split("\n")
                
            dburl = 'mysql+pymysql://%s:%s@%s/%s' % (myuser, mypwd, myhost, mydb)
            engine = create_engine(dburl, echo=args.db_echo)
            Base.metadata.create_all(engine)
            Session = sessionmaker(bind=engine)
            self.session = Session()

        else:
            self.session = args.db_session["_"]

        with TemporaryDirectory() as self.tempdir:
            if os.path.isdir(inputpath):
                for item in os.listdir(inputpath):
                    self.loaddb_e3smexp(os.path.join(inputpath, item))

            elif os.path.isfile(inputpath):
                self.loaddb_e3smexp(inputpath)

            else:
                print("Can't find input path: %s" % inputpath, file=sys.stderr)
                sys.exit(-1)

def insertInputs(zipfile,db,expid, stdout, stderr=None):

    with TemporaryDirectory() as tempdir:
        if os.path.isdir(zipfile):
            for item in os.listdir(zipfile):
                print(item)
                #loaddb_e3smexp(os.path.join(zipfile, item),db,expid)

        elif os.path.isfile(zipfile):
            print("isfile------->")
            loaddb_e3smexp(zipfile,db,expid)

        else:
            print("Can't find input path: %s" % zipfile, file=sys.stderr)
            sys.exit(-1)
            
    return 0

if __name__ == "__main__":
    db=0
    expid=0
    insertInputs(sys.argv[1],db,expid, sys.stdout, sys.stderr)








#old version
#def insertInputs(zipfile, stdout, stderr=None):
    """parse e3sm input data and upload to pace database

    Parameters:
    zipfile(str): file path to a zipped e3sm data
    
    dbcfg is hardcoded for now
    dbcfg(str): file path to a pace database configuration ascii data.
                Only one item should exist in a line in four lines in total::

                    username
                    password
                    hostname
                    databasename

    stdout(file object): output file object
    stderr(file object): error file object. Optional

    Returns:
    int: return code

    Notes:
    * As of this version, this function works only if e3smlab is installed
        in Python 3. To make sure that e3smlab is installed in Python 3,
        use following command to install::

        python3 -m pip install e3smlab

    * This function assumes that e3smexp table exists and the table already
        has the expid of this zipped data. It may require to commit any staged
        transaction before calling this function.
    """

    #import subprocess
    #cmd = ["/opt/venv/pace3/bin/e3smlab", "pacedb", zipfile, "--db-cfg", "/pace/prod/portal/pace/e3smlabdb.cfg", "--commit"]
    # print ("Calling " + str(cmd) )
    #return subprocess.call(cmd, stdout=stdout, stderr=stderr)

