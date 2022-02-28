#! /usr/bin/env python3
# @file parseBuildTime.py
# @brief parser for build_times.
# @author Gaurab KC
# @version 3.0
# @date 2022-02-08
'''
This function reads the build_times and then stores the the json object to DB
'''
import gzip

def loaddb_buildTimesFile(buildfile):
    try:
        data = {}
        with gzip.open(buildfile, 'rt') as f:
            f.readline()  # skip first line for header information
            for line in f:
                value = line.split()
                if value[0] in data:
                    data[value[0]]+=float(value[1])
                else:
                    data[value[0]]=float(value[1])
        f.close()
        return data
    except:
        print("Something went wrong with %s" %buildfile)