#! /usr/bin/env python3
# @file parseScorpioStats.py
# @brief parser for scorpio_stat file.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13


import tarfile, sys, json
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
This function returns the IO model component name having maximum tot_time.
'''
def getMax(data):
    modelData = data["ScorpioIOSummaryStatistics"]["ModelComponentIOStatistics"]

    max_comp = float('-inf')
    output = None

    for mdata in modelData:

        if 'tot_time(s)' in mdata and mdata['tot_time(s)']>max_comp:
            max_comp = mdata['tot_time(s)']
            output = mdata['name']
    
    if output:
        output = output.split()[-1]

    return output

def getIO(data, runTime):
    iotime = None
    iopercent = None

    iotime = float(data["ScorpioIOSummaryStatistics"]["OverallIOStatistics"]["tot_time(s)"])
    iopercent = round((iotime/runTime)*float(100.0),2)

    return iotime, iopercent

'''
This function checks for supported scorpio stats file
'''
def supportedVersion(data):
    model = data["ScorpioIOSummaryStatistics"]["OverallIOStatistics"]
    if "tot_time(s)" in model:
        return True
    else:
        return False

def versionTag(data):
    model = data["ScorpioIOSummaryStatistics"]["OverallIOStatistics"]
    if "spio_stats_version" in model:
        return model["spio_stats_version"]
    else:
        return None

'''
This function reads the scorpio file and return data in json format
'''
def loaddb_scorpio_stats(spiofile, runTime):

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
        
        oldsupported = 0
        for file in Scorpio_files:
            
            model = {
                'name':None,
                'data':None,
                'iopercent':None,
                'iotime':None,
                'version':None
            }
            name = None
            jsondata = None
            iopercent = None
            iotime = None
            version = None

            name = (file.name).split('/')[-1].split('_')[-1].split('.')[0]
            jsondata = sptar.extractfile(file).read()

            if name and jsondata:
                jsondatapython = json.loads(jsondata)
                if not supportedVersion(jsondatapython):
                    print('Encountered very old format of Scorpio stats which is not supported.')
                    continue
                iotime,iopercent = getIO(jsondatapython, float(runTime))
                version = versionTag(jsondatapython)
                if iopercent>100 or (version==None and oldsupported>=10):
                    continue
                if version==None:
                    oldsupported+=1
                max_component = getMax(jsondatapython)
                model['name'] = str(max_component)+'-'+str(name)
                model['data'] = jsondata
                model['iopercent'] = iopercent
                model['iotime'] = iotime
                model['version'] = version
                data.append(model)
        return data
    except:
       print("Error encountered while parsing scorpio file : %s" %spiofile)
