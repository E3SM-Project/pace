import sys, os, shutil, json, typing, tarfile
from . datastructs import *
from tempfile import TemporaryDirectory
from zipfile import ZipFile
import gzip
import f90nml, xmltodict


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

def unzip(infile,outfile):

    with gzip.open(infile, 'rb') as f_in:
        with open(outfile,'wb') as f_out:
            shutil.copyfileobj(f_in,f_out)
        f_in.seek(0)
    f_out.close()
    f_in.close()


def loaddb_scorpio_stats(expid, name, spiofile,db):

    # TODO: handle a direcotry generated from this gz file
    # TODO: select a json file
    try:
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
        
        spio = db.session.query(ScorpioStats).filter_by(
            expid=expid, name=name).first()
        
        if spio:
            print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

        elif jsondata is None:
            print("Json data read error: expid=%d, name=%s" % (expid, name))

        else:
            spio = ScorpioStats(expid=expid, name=name, data=jsondata)
            db.session.add(spio)
    except:
        print("Something went wrong with %s" %spiofile)
    
def loaddb_memfile(expid, name, memfile, db):
    
    try:
        with gzip.open(memfile, 'rt') as f:
            csv_data = f.read()
        #print(csv_data)
        mem = db.session.query(MemfileInputs).filter_by(
                expid=expid, name=name).first()

        if mem:
            print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

        else:
            mem = MemfileInputs(expid=expid, name=name, data=csv_data)
            db.session.add(mem)
    except:
        print("Something went wrong with %s" %memfile)
    
def loaddb_rcfile(expid, name, rcpath, db):

    try:
        rcitems = []
        with gzip.open(rcpath, 'rt') as f_in:
            for line in f_in.read().strip().split("\n"):
                items = tuple(l.strip() for l in line.split(":"))

                if len(items)==2:
                    rcitems.append('"%s":%s' % items)
        f_in.close()
        
        jsondata = "{%s}" % ",".join(rcitems) 
        
        #try:
        rc = db.session.query(RCInputs).filter_by(
                expid=expid, name=name).first()

        if rc:
            print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

        else:
            rc = RCInputs(expid=expid, name=name, data=jsondata)
            db.session.add(rc)
    except:
        print("Something went wrong with %s" %rcpath)

    #except (InvalidRequestError, IntegrityError) as err:
    #    print("Missing expid in database: expid=%d, rc-name=%s" % (expid, name))

def loaddb_xmlfile(expid, name, xmlpath, db):
    
    from xml.parsers.expat import ExpatError

    try:
        outputpath = xmlpath[:-3]
        unzip(xmlpath,outputpath)
        with open(outputpath) as f:
            data = f.read()
        xmldict = xmltodict.parse(data)
        jsondata = json.dumps(xmldict)
        
        xml = db.session.query(XMLInputs).filter_by(
                expid=expid, name=name).first()

        if xml:
            print("Insertion is discarded due to dupulication: expid=%d, xml-name=%s" % (expid, name))

        else:
            xml = XMLInputs(expid=expid, name=name, data=jsondata)
            db.session.add(xml)
        
    except ExpatError as err:
        print("Warning: %s" % str(err))
    
    except:
        print("Something went wrong with %s" %xmlpath)
    
    #except (InvalidRequestError, IntegrityError) as err:
    #    print("Missing expid in database: expid=%d, xml-name=%s" % (expid, name))

    #except Exception as err:
    #    print("Warning: %s" % str(err))
    #    import pdb; pdb.set_trace()
    #    print(err)

def loaddb_namelist(expid, name, nmlpath,db):
    
    jsondata = None

    try:
        outputpath = nmlpath[:-3]
        unzip(nmlpath,outputpath)
        nml_parser = f90nml.Parser()
        nml = nml_parser.read(outputpath)
        data=nml.todict(complex_tuple=True)
        jsondata = json.dumps(data)
    except IndexError as err:
        if name.startswith("user_nl"):
            jsondata = ""

        else:
            #import pdb; pdb.set_trace()
            raise err
            
    except StopIteration as err:
        print("-----StopIteration-------")
        print("Warning: %s" % str(err))

    except Exception as err:
        print("Warning: %s" % str(err))
        #import pdb; pdb.set_trace()
        print("-----exception error------")
        print(err)
    
    #try:
    nml = db.session.query(NamelistInputs).filter_by(
                expid=expid, name=name).first()
    if nml:
        print("Insertion is discarded due to dupulication: expid=%d, name=%s" % (expid, name))

    else:
        nml = NamelistInputs(expid=expid, name=name, data=jsondata)
        db.session.add(nml)
    
        

    #except (InvalidRequestError, IntegrityError) as err:
    #    print("Missing expid in database: expid=%d, namelist-name=%s" % (expid, name))

def loaddb_casedocs(expid, casedocpath,db):

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
                    loaddb_namelist(expid, name, path,db)

                elif nameseq[0] in xmlfiles:
                    loaddb_xmlfile(expid, name, path,db)

                elif nameseq[0] in rcfiles:
                    loaddb_rcfile(expid, name, path,db)

                else:
                    pass
        else:
            pass

def loaddb_e3smexp(zippath,tempdir,db,expid):

    head, tail = os.path.split(zippath)
    basename, ext = os.path.splitext(tail)
    items = basename.split("-")
    
    if ext == ".zip" and len(items)==3:

        with ZipFile(zippath) as myzip:

            unzipdir = os.path.join(tempdir, basename)
            myzip.extractall(path=unzipdir)

            #try:
            for item in os.listdir(unzipdir):
                if item.startswith(".") or item in exclude_zipfiles:
                    continue

                basename, ext = os.path.splitext(item)
                path = os.path.join(unzipdir, item)

                if os.path.isdir(path):

                    if basename.startswith("CaseDocs"):
                        loaddb_casedocs(expid, path,db)
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

                    if nameseq:
                        if nameseq[0] in spiofiles:
                            loaddb_scorpio_stats(expid, name, path,db)
                            #print("spio")
                        elif nameseq[0] in memfiles:
                            loaddb_memfile(expid, name, path,db)    

                    else:
                        pass
                else:
                    pass

            #except (InvalidRequestError, IntegrityError) as err:
            #    print("Warning: database integrity error at %s: %s" % (zippath, str(err)))

            #finally:                
            shutil.rmtree(unzipdir, ignore_errors=True)

def insertInputs(zipfile,db,expid, stdout, stderr=None):

    with TemporaryDirectory() as tempdir:
        if os.path.isdir(zipfile):
            for item in os.listdir(zipfile):
                print(item)
                loaddb_e3smexp(os.path.join(zipfile, item),tempdir,db,expid)

        elif os.path.isfile(zipfile):
            loaddb_e3smexp(zipfile,tempdir,db,expid)

        else:
            print("Can't find input path: %s" % zipfile, file=sys.stderr)
            
    return 0

if __name__ == "__main__":
    db=0
    expid=0
    insertInputs(sys.argv[1],db,expid, sys.stdout, sys.stderr)
