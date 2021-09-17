#! /usr/bin/env python3
# @file parseModelVersion.py
# @brief parser for GIT_DESCRIBE file to grab the model version.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import gzip, sys

# parser for GIT_DESCRIBE file
def parseModelVersion(gitfile):
    # open file
    if gitfile.endswith('.gz'):
        parsefile = gzip.open(gitfile,'rt')
    else:
        parsefile = open(gitfile, 'rt')
    # initialize version
    version = 0
    for line in parsefile:
        if line != '\n':
            version = line.strip('\n')
            break
    parsefile.close()
    return version

if __name__ == '__main__':
    if len(sys.argv)>1:
        filename = sys.argv[1]
    else:
        filename = '/Users/4g5/Downloads/exp-blazg-71436/GIT_DESCRIBE.43235257.210608-222102.gz'
    print(parseModelVersion(filename))