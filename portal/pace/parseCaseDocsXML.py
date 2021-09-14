#! /usr/bin/env python3
# @file parseCaseDocsXML.py
# @brief parser for XML files in CaseDocs.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import gzip, shutil, xmltodict, json, sys

def unzip(infile,outfile):

    with gzip.open(infile, 'rb') as f_in:
        with open(outfile,'wb') as f_out:
            shutil.copyfileobj(f_in,f_out)
        f_in.seek(0)
    f_out.close()
    f_in.close()

def loaddb_xmlfile(xmlpath):
    
    from xml.parsers.expat import ExpatError

    try:
        outputpath = xmlpath[:-3]
        unzip(xmlpath,outputpath)
        with open(outputpath) as f:
            data = f.read()
        xmldict = xmltodict.parse(data)
        jsondata = json.dumps(xmldict)
        return jsondata
        
    except ExpatError as err:
        print("Warning: %s" % str(err))
    
    except:
        print("Something went wrong with %s" %xmlpath)
    

if __name__ == "__main__":
    xmlpath = sys.argv[1]
    print(loaddb_xmlfile(xmlpath))