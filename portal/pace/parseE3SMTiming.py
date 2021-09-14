#! /usr/bin/env python3
# @file parseE3SMTiming.py
# @brief parser for E3SM timing file.
# @author Gaurab KC
# @version 3.0
# @date 2021-09-13

import gzip, sys
from sqlalchemy.exc import SQLAlchemyError

# converts path string into single file name (/home/absd/asde/file.txt -> file.txt)
def convertPathtofile(path):
    if '/' in path:
        foldername = path.split('/')
        return (foldername[len(foldername)-1]) #grab the last file from path link
    else:
        return path

# removes unwanted spaces (dedicated for parsing model_timing files)
def spaceConcat(phraseIn,subGroup = False,filter="\n\t"):
    phraseIn = phraseIn.strip(filter)
    #Destroy spaces by default:
    phraseSplit = phraseIn.split(" ")
    total=[""]
    currPhrase = 0
    onWord = False
    firstPhrase = True
    for i in range(len(phraseSplit)):
        if onWord or not phraseSplit[i] == "":
            if not onWord:
                onWord = True
                if not subGroup or not firstPhrase:
                    total.append("")
            firstPhrase = False
            addWord = True
            #Ignore newlines:
            if phraseSplit[i]  == "":
                onWord = False
                addWord = False
                if subGroup:
                    currPhrase+=1
            if addWord:
                if not len(total[currPhrase]) == 0:
                    total[currPhrase]+=" "
                total[currPhrase]+=phraseSplit[i]
    return total

# Returns a list of items from the table.
def tableParse(lineInput):
    names=["component","comp_pes","root_pe","tasks","threads","instances","stride"]
    resultList=[]
    for item in lineInput:
        splitValues = spaceConcat(item,True)
        tableColumn={}
        for i in range(len(names)):
            tableColumn[names[i]] = splitValues[i].strip("(")
        resultList.append(tableColumn)
    return resultList


def parseE3SMtiming(filename):
    # Flags are set to False at beginning, success is marked True only at the end
    successFlag = False
    duplicateFlag = False
    currExpObj = None
    # open file
    if filename.endswith('.gz'):
        parseFile=gzip.open(filename,mode='rt')
    else:
        parseFile=open(filename,'rt')

    # dictionary to store timingprofile
    timingProfileInfo={}
    # list to store component table
    componentTable=[]
    # list to store runtime table
    runTimeTable=[]
    # tmp var for parsing purpose
    word=''

    try:
        count = 0
        for line in parseFile:
            count = count + 1
            if line!='\n':
                # find values for given keys
                if len(timingProfileInfo)<12:
                    word=line.split(':', 2)
                    # if 'Case' in word[0]:
                    # You can't use if 'Case' in word[0] as that would also match caseroot
                    # This was a pretty difficult to debug bug - Sarat April 4, 2019.
                    if word[0].strip() =='Case':
                        timingProfileInfo['case']=word[1].strip()
                        # print timingProfileInfo['case']
                    elif 'LID' in word[0]:
                        timingProfileInfo['lid']=word[1].strip()
                        # print timingProfileInfo['lid']
                    elif 'Machine' in word[0]:
                        timingProfileInfo['machine']=word[1].strip()
                        # print timingProfileInfo['machine']
                    elif 'Caseroot' in word[0]:
                    # elif word[0].strip() == 'Caseroot':
                    # elif word[0]=='Caseroot':
                        timingProfileInfo['caseroot']=word[1].strip()
                        # print timingProfileInfo['caseroot']
                    elif 'Timeroot' in word[0]:
                        timingProfileInfo['timeroot']=word[1].strip()
                        # print timingProfileInfo['timeroot']
                    elif 'User' in word[0]:
                        timingProfileInfo['user']=word[1].strip()
                        # print timingProfileInfo['user']
                    elif 'Curr' in word[0]:
                        newWord = line.split(None,3)
                        timingProfileInfo['curr']=newWord[3].strip()
                        # print timingProfileInfo['curr']
                    elif 'grid' in word[0]:
                        timingProfileInfo['long_res']=word[1].strip()
                        # print timingProfileInfo['long_res']
                    elif 'compset' in word[0]:
                        timingProfileInfo['long_compset']=word[1].strip()
                        # print timingProfileInfo['long_compset']
                    elif 'stop' in word[0]:
                        # stop option or stop_option : ndays, stop_n = 20
                        newWord=word[1].split(",")
                        timingProfileInfo['stop_option']=newWord[0].strip()
                        # print timingProfileInfo['stop_option']
                        if 'stop_n' in newWord[1]:
                            newWord2 = newWord[1].split('=')
                            timingProfileInfo['stop_n'] = newWord2[1].strip()
                            # print timingProfileInfo['stop_n']
                    elif 'length' in word[0]:
                        #   run length  : 20 days (19.9166666667 for ocean)
                        newWord=word[1].split("(")
                        # Now you get 20 days etc
                        newWord2=newWord[0].strip().split(" ")
                        timingProfileInfo['run_length']=newWord2[0]

                flagrun=False
                flaginit=False
                flagfinal=False
                word=line.split(None,1)
                if word[0]=='total':
                    newWord=word[1].split(":")
                    newWord1=newWord[1].split(" ")
                    timingProfileInfo['total_pes']=newWord1[1]
                elif word[0]=='mpi':
                    newWord=word[1].split(":")
                    newWord1=newWord[1].split(" ")
                    timingProfileInfo['mpi_task']=newWord1[1]
                elif word[0]=='pe':
                    newWord=word[1].split(":")
                    newWord1=newWord[1].split(" ")
                    timingProfileInfo['pe_count']=newWord1[1]
                elif word[0]=='Model':
                    newWord=word[1].split(":")
                    newWord1=newWord[1].split()
                    if 'model_cost' in list(timingProfileInfo.keys()):
                        timingProfileInfo['model_throughput']=newWord1[0]
                    else:
                        timingProfileInfo['model_cost']=newWord1[0]
                elif word[0]=='Actual':
                    newWord=word[1].split(":")
                    newWord1=newWord[1].split()
                    timingProfileInfo['actual_ocn']=newWord1[0]
                elif word[0]=='Init' and flaginit == False:
                    newWord=word[1].split(":")
                    newWord1=newWord[1].split()
                    timingProfileInfo['init_time']=newWord1[0]
                    flaginit = True
                elif word[0]=='Run' and flagrun == False:
                    newWord=word[1].split(":")
                    newWord1=newWord[1].split()
                    timingProfileInfo['run_time']=newWord1[0]
                    flagrun = True
                elif word[0]=='Final' and flagfinal == False:
                    newWord=word[1].split(":")
                    newWord1=newWord[1].split()
                    timingProfileInfo['final_time']=newWord1[0]
                    flagfinal = True
                elif len(timingProfileInfo)>=20:
                    break

    except IndexError as e:
        print(('    ERROR: %s' %e))
        parseFile.close()
        return (successFlag, duplicateFlag, currExpObj) # skips this experiment
    except KeyError as e:
        print(('    ERROR: Missing data %s' %e))
        parseFile.close()
        return (successFlag, duplicateFlag, currExpObj) # skips this experiment
    except Exception as e:
        print(('    ERROR: %s' %e))
        print(('    ERROR: Something is wrong with %s' %convertPathtofile(filename)))
        parseFile.close()
        return (successFlag, duplicateFlag, currExpObj) # skips this experiment

    parseFile.close()

    # open file again to parse component and runtime tables
    try:
        if filename.endswith('.gz'):
            parseFile=gzip.open(filename,'rt')
        else:
            parseFile=open(filename,'rt')
        lines=parseFile.readlines()
        componentTableSuccess = False
        runtimeTableSuccess = False
        component=[]
        tablelist=[]
        # loop to grab component and store in a list and parse runtime table
        for i in range(len(lines)):
            if lines[i] != '\n':
                firstWord = lines[i].split()[0]
                if firstWord == 'component':
                    for j in range(9):
                        tablelist.append(lines[i+j+2])
                    componentTableSuccess = True
                # parse runtime table and store in a list
                elif firstWord == 'TOT':
                    for j in range(11):
                        component=lines[i+j].split()
                        if component[1]=='Run':
                            runTimeTable.append(component[0])
                        else:
                            runTimeTable.append(str(component[0])+'_COMM')
                        runTimeTable.append(component[3])
                        runTimeTable.append(component[5])
                        runTimeTable.append(component[7])
                        runtimeTableSuccess = True
            # grabbed both tables then break
            if componentTableSuccess == True and runtimeTableSuccess == True:
                break
        # check if both table exists
        if componentTableSuccess != True or runtimeTableSuccess != True:
            print('    ERROR: runtime/component table not found')
            return False

        # parse component table
        resultlist=tableParse(tablelist)
        parseFile.close()

        # store component table values in a list
        for i in range(len(tablelist)):
            tmpthread1=resultlist[i]['component']
            change1=tmpthread1.split(" ")
            componentTable.append(change1[0])
            componentTable.append(resultlist[i]['comp_pes'])
            componentTable.append(resultlist[i]['root_pe'])
            componentTable.append(resultlist[i]['tasks'])
            tmpthread=resultlist[i]['threads']
            change=tmpthread.split(" ")
            componentTable.append(change[1])
            componentTable.append(resultlist[i]['instances'])
            componentTable.append(resultlist[i]['stride'])

        """print('-----------timingProfileInfo----------')
        print(timingProfileInfo)
        print('--------------componentTable---------')
        print(componentTable)
        print('-------------runTimeTable------------')
        print(runTimeTable)"""
        successFlag = True
        return(successFlag, timingProfileInfo, componentTable, runTimeTable)
    except IndexError as e:
        print(('    ERROR: %s' %e))
        # Sarat: Rollback added to avoid auto-incrementing expid for failed uploads
        # Check if rollback doesn't cause issues with skipping incomplete exps
        #db.session.rollback()
        parseFile.close()
        return (successFlag, duplicateFlag, currExpObj) # skips this experiment
    except KeyError as e:
        print(('    ERROR: Missing data %s' %e))
        #db.session.rollback()
        parseFile.close()
        return (successFlag, duplicateFlag, currExpObj) # skips this experiment
    except SQLAlchemyError as e:
        error = str(e.__dict__['orig'])
        print(('    SQL ERROR: %s' %e))
        #db.session.rollback()
        parseFile.close()
        return (successFlag, duplicateFlag, currExpObj) # skips this experiment
    except Exception as e:
        print(('    ERROR: %s' %e))
        print(('    ERROR: something is wrong with %s' %convertPathtofile(filename)))
        #db.session.rollback()
        parseFile.close()
        return (successFlag, duplicateFlag, currExpObj) # skips this experiment

if __name__ == "__main__":
    if sys.argv[1]:
        filename = sys.argv[1]
    else:
        filename = "/Users/4g5/Downloads/exp-blazg-71436/e3sm_timing.e3sm_v1.2_ne30_noAgg-60.43235257.210608-222102.gz"
    parseE3SMtiming(filename)