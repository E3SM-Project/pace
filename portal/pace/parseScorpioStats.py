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

def loaddb_scorpio_stats(spiofile):

    # TODO: handle a direcotry generated from this gz file
    # TODO: select a json file
    try:
        sptar = tarfile.open(spiofile, "r:gz")
        
        jsonmember = None
        jsondata = None

        members = safemembers(sptar)
        for member in members:
            if member.isfile() and member.name.endswith("json"):
                if jsonmember is None or jsonmember.size < member.size:
                    jsonmember = member
        
        if jsonmember:
            jsondata = sptar.extractfile(jsonmember).read()
        
        sptar.close()

        if jsondata is None:
            print("Json data read error: filename=%s" %spiofile)
        else:
            return jsondata
    except:
        print("Something went wrong with %s" %spiofile)

if __name__ == "__main__":
    if len(sys.argv)>1:
        filename = sys.argv[1]
    else:
        filename = "/Users/4g5/Downloads/exp-ac.golaz-73642/spio_stats.63117.210714-233452.tar.gz"
    print(loaddb_scorpio_stats(filename))