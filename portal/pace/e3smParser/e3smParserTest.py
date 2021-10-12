#! /usr/bin/env python3
# @file parseE3SMTiming.py
# @brief parser for E3SM timing file.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import sys

import parseE3SMTiming, parseMemoryProfile, parseModelVersion, parseNameList, parseRC, parseReadMe, parseScorpioStats, parseXML

if __name__ == "__main__":
    filename = "/Users/4g5/Downloads/exp-blazg-71436/e3sm_timing.e3sm_v1.2_ne30_noAgg-60.43235257.210608-222102.gz"
    print(parseE3SMTiming.parseE3SMtiming(filename))
    
    filename = "/Users/4g5/Downloads/exp-ac.golaz-73642/memory.3.86400.log.63117.210714-233452.gz"
    print(parseMemoryProfile.loaddb_memfile(filename))

    filename = '/Users/4g5/Downloads/exp-blazg-71436/GIT_DESCRIBE.43235257.210608-222102.gz'
    print(parseModelVersion.parseModelVersion(filename))

    filename = "/Users/4g5/Downloads/exp-ac.golaz-73642/CaseDocs.63117.210714-233452/atm_in.63117.210714-233452.gz"
    print(parseNameList.loaddb_namelist(filename))

    filename = "/Users/4g5/Downloads/exp-ac.golaz-73642/CaseDocs.63117.210714-233452/seq_maps.rc.63117.210714-233452.gz"
    print(parseRC.loaddb_rcfile(filename))

    filename = "/Users/4g5/Downloads/exp-blazg-71436/CaseDocs.43235257.210608-222102/README.case.43235257.210608-222102.gz"
    print(parseReadMe.parseReadme(filename))

    filename = "/Users/4g5/Downloads/exp-ac.golaz-73642/spio_stats.63117.210714-233452.tar.gz"
    print(parseScorpioStats.loaddb_scorpio_stats(filename))

    filename = "/Users/4g5/Downloads/exp-ac.golaz-73642/CaseDocs.63117.210714-233452/env_batch.xml.63117.210714-233452.gz"
    print(parseXML.loaddb_xmlfile(filename))