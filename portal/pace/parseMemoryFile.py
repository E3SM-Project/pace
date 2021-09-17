#! /usr/bin/env python3
# @file parseMemoryFile.py
# @brief parser for memory file.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import gzip, sys

def loaddb_memfile(memfile):
    
    try:
        csv_data = None
        with gzip.open(memfile, 'rt') as f:
            csv_data = f.read()
        return csv_data
    except:
        print("Something went wrong with %s" %memfile)

if __name__ == "__main__":
    if len(sys.argv)>1:
        filename = sys.argv[1]
    else:
        filename = "/Users/4g5/Downloads/exp-ac.golaz-73642/memory.3.86400.log.63117.210714-233452.gz"
    print(loaddb_memfile(filename))