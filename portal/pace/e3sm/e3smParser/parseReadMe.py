#! /usr/bin/env python3
# @file parseReadMe.py
# @brief parser for ReadMe file.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import gzip, sys

# converts path string into single file name (/home/absd/asde/file.txt -> file.txt)
def convertPathtofile(path):
    if '/' in path:
        foldername = path.split('/')
        return (foldername[len(foldername)-1]) #grab the last file from path link
    else:
        return path

# parser for readme file
def parseReadme(readmefilename):
    # open file
    if readmefilename.endswith('.gz'):
        fileIn=gzip.open(readmefilename,'rt')
    else:
        fileIn = open(readmefilename,'rt')
    resultElement = {}
    commandLine = None
    flag=False
    try:
        for commandLine in fileIn:
            word=commandLine.split(" ")
            for element in word:
                # this line holds profile information
                if ('create_newcase' in element):
                    cmdArgs = commandLine.split(": ",1)[1].strip("./\n").split(" ")
                    resultElement["name"] = cmdArgs[0]
                    for i in range(len(cmdArgs)):
                        if cmdArgs[i][0] == "-":
                            if "=" in cmdArgs[i]:
                                argumentStr = cmdArgs[i].strip("-").split("=")
                                resultElement[argumentStr[0]] = argumentStr[1]
                            else:
                                argument = cmdArgs[i].strip("-")
                                if i+1 < len(cmdArgs):
                                    resultElement[argument] = cmdArgs[i+1]
                        resultElement["date"] = commandLine.split(": ",1)[0].strip(":")
                    break
            # job done after finding elements res, compset
            if 'res' and 'compset' in list(resultElement.keys()):
                break
        # this case only runs if element 'res','compset' exists else throws keyError
        if resultElement['res'] is None:
            resultElement['res'] = 'nan'
        if resultElement['compset'] is None:
            resultElement['compset'] = 'nan'
    except KeyError as e:
        print(('[ERROR]: %s not found in %s' %(e,convertPathtofile(readmefilename))))
        fileIn.close()
        return False
    except IndexError as e:
        print(('[ERROR]: %s in file %s' %(e,convertPathtofile(readmefilename))))
        fileIn.close()
        return False
    except Exception as e:
        print(('[ERROR]: %s' %e))
        print(('    Error encountered while parsing README.docs : %s' %convertPathtofile(readmefilename)))
        fileIn.close()
        return False
    fileIn.close()
    return resultElement
