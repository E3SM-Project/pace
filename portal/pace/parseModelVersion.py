import gzip

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
    filename = '/Users/4g5/Downloads/exp-blazg-71436/GIT_DESCRIBE.43235257.210608-222102.gz'
    print(parseModelVersion(filename))