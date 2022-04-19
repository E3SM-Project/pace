#! /usr/bin/env python3
# @file parseMemoryFile.py
# @brief parser for memory file.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import gzip

'''
    This function reads the memory file data and returns the cvs data
'''
def loaddb_memfile(memfile):
    
    try:
        csv_data = None
        with gzip.open(memfile, 'rt') as f:
            csv_data = f.read()
        return csv_data
    except:
        print("Error encountered while parsing memory file : %s" %memfile)
