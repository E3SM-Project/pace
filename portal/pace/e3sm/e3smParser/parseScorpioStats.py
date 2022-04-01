#! /usr/bin/env python3
# @file parseScorpioStats.py
# @brief parser for scorpio_stat file.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import tarfile, sys
from os.path import abspath, realpath, dirname, join as joinpath
resolved = lambda x: realpath(abspath(x))

def badpath(path, base):
    # joinpath will ignore base if path is absolute
    return not resolved(joinpath(base,path)).startswith(base)

def badlink(info, base):
    # Links are interpreted relative to the directory containing the link
    tip = resolved(joinpath(base, dirname(info.name)))
    return badpath(info.linkname, base=tip)

def safemembers(members):
    base = resolved(".")

    for finfo in members:
        if badpath(finfo.name, base):
            print(finfo.name, "is blocked (illegal path)",file=sys.stderr)
        elif finfo.issym() and badlink(finfo,base):
            print(finfo.name, "is blocked: Hard link to", finfo.linkname,file=sys.stderr)
        elif finfo.islnk() and badlink(finfo,base):
            print(finfo.name, "is blocked: Symlink to", finfo.linkname, file=sys.stderr)
        else:
            yield finfo

'''
This function reads the scorpio file and return data in json format
'''
def loaddb_scorpio_stats(spiofile):

    # TODO: handle a direcotry generated from this gz file
    # TODO: select a json file
    try:
        sptar = tarfile.open(spiofile, "r:gz")
        data = []
        Scorpio_files = []

        members = safemembers(sptar)
        for member in members:
            if member.isfile() and member.name.endswith("json"):
                Scorpio_files.append(member)
        
        for file in Scorpio_files:
            
            model = {
                'name':None,
                'data':None
            }
            name = None
            jsondata = None

            name = (file.name).split('/')[-1].split('_')[-1].split('.')[0]
            jsondata = sptar.extractfile(file).read()

            if name and jsondata:
                model['name'] = name
                model['data'] = jsondata
                data.append(model)
        return data
    except:
        print("Something went wrong with %s" %spiofile)