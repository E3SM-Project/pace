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
    print(loaddb_memfile(sys.argv[1]))