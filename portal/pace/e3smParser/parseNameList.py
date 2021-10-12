#! /usr/bin/env python3
# @file parseCaseDocsNameList.py
# @brief parser for namelist file under CaseDocs.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import f90nml, json, gzip, shutil, sys

def unzip(infile,outfile):

    with gzip.open(infile, 'rb') as f_in:
        with open(outfile,'wb') as f_out:
            shutil.copyfileobj(f_in,f_out)
        f_in.seek(0)
    f_out.close()
    f_in.close()

def loaddb_namelist(nmlpath):
    
    jsondata = None

    try:
        outputpath = nmlpath[:-3]
        unzip(nmlpath,outputpath)
        nml_parser = f90nml.Parser()
        nml = nml_parser.read(outputpath)
        data=nml.todict(complex_tuple=True)
        jsondata = json.dumps(data)
        return jsondata
    except IndexError as err:
        name = outputpath.split('/')[-1]
        if name.startswith("user_nl"):
            jsondata = ""
            return jsondata

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
