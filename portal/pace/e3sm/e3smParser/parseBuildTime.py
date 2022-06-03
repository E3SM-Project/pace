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
        total_computecost = 0
        total_elapsed_time = 0
        with gzip.open(buildfile, 'rt') as f:
            f.readline()  # skip first line for header information
            for line in f:
                value = line.split()
                if value[0] in data:
                    data[value[0]]+=float(value[1])
                else:
                    data[value[0]]=float(value[1])
                total_computecost+=float(value[1])
        if 'Total_Elapsed_Time' in data:
            total_elapsed_time = data['Total_Elapsed_Time']
            total_computecost-=total_elapsed_time
        f.close()
        if data == {}:
            return None, total_computecost,total_elapsed_time
        return data,total_computecost, total_elapsed_time
    except:
        print("Error encountered while parsing build time file : %s" %buildfile)
        return None, None