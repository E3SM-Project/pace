##
# @file modelTiming.py
# @brief Parse files that come from GPTL into JSON for storing in DB.
# @author Zachary Mitchell, Sarat Sreepathi
# @version 2.0
# @date 2019-07-26

import types,json,os.path
from os import listdir

#This is a list of configurations that tell the parser how to read specific GPTL files
# Reference: https://github.com/E3SM-Project/pace/blob/master/portal/pace/mtConfig/specification.md
# Sarat (July 26, 2019): Changed variable names (names,altNames)->(fileCols,outCols) to avoid confusion.
parserConfigs = {
"e3sm":[{
        "fileCols":["On","Called","Recurse","Wallclock","max","min","UTR Overhead"],
        "outCols":["on","called","recurse","wallClock","max","min","utrOverhead"],
        "startMarker":["Stats for thread",2],
        "fileIdentifiers":["Stats for thread"],
        "rootParent":2
    },
    # GPTL timing stats v2 (new col added 'on')
    {
        "fileCols":["on", "process","threads","count","walltotal","wallmax","wallmin"],
        "outCols":["on", "processes","threads","count","walltotal","wallmax","wallmax_proc","wallmax_thrd","wallmin","wallmin_proc","wallmin_thrd"],
        "startMarker":["name",1],
        "fileIdentifiers":["'on' indicates whether the timer was active during output", "GLOBAL STATISTICS"],
        "rootParent":0
    },
    # GPTL timing stats v1 (org)
    {
        "fileCols":["process","threads","count","walltotal","wallmax","wallmin"],
        "outCols":["processes","threads","count","walltotal","wallmax","wallmax_proc","wallmax_thrd","wallmin","wallmin_proc","wallmin_thrd"],
        "startMarker":["name",1],
        "fileIdentifiers":["GLOBAL STATISTICS"],
        "rootParent":0
    }]
}

class timeNode(object):
    #Without this, a reeealy weird scoping problem happens; not sure why.
    def __init__(self):
        self.name="default"
        self.multiParent = False
        self.values={}
        self.children=[]
        self.parent = self #Should this refer to itself... or have none?


def loadConfig(files,appendLocation = None):
    """
    "files": directory path, json file, file object. OR list of any of the former.
    appendLocation: "default", dictionary
    
    This function sets up one or more configuration files for use in describing a GPTL file.
    """
    #A configuration can be used in the short-term, or throughout the time this script is kept imported (e.g for a flask application ;P).
    #This allows for custom configurations without taking up ram from the system.
    targetConfig = {}
    if appendLocation == "default":
        targetConfig = parserConfigs
    elif not appendLocation == None:
        targetConfig = appendLocation
    #To stay "dry", here are some nested functions to avoid repetetiveness:

    #Add json to targetConfig
    def appendJson(jsonFile):
        srcJson = json.loads(jsonFile.read())
        for key in srcJson.keys():
            if key not in targetConfig.keys():
                targetConfig[key] = srcJson[key]
    #Check if this is a valid json file
    def isJsonFile(path):
        jsonTest = path.rsplit(".",1)
        return os.path.isfile(path) and len(jsonTest) > 1 and jsonTest[1] == "json"

    fileList = []
    if type(files) == types.ListType:
        fileList = files
    else:
        fileList.append(files)
    for element in fileList:
        if type(element) == types.FileType:
            appendJson(element)
        elif type(element) == types.StringType:
            #Figure out if it's a directory or not:
            if isJsonFile(element):
                appendJson(open(element))
            elif os.path.isdir(element):
                for filePath in listdir(element):
                    # print(element+"/"+filePath)
                    if isJsonFile(element+"/"+filePath):
                        appendJson(open(element+"/"+filePath))
    return targetConfig

def detectMtFile(fileObj,configList = parserConfigs):
    #This returns the matching configuration of this file, along with the proper indexes to start getting the file's lines
    lineCount = 0
    threadIndexes=[]
    currLine = ""
    targetConfig = None

    # For each config, check file match and column names match
    # Initialize matching file scores and column scores to zero for each configuration
    filescore = []
    colscore = []
    for key in configList.keys():
        for config in configList[key]:
            myconfigIdx = configList[key].index(config)
            filescore.append(0)
            colscore.append(0)

    currLine = fileObj.readline()
    while not currLine == "":
        lineCount+=1
        #Scan every line to find everything we should know about the file:
        if targetConfig == None:
            for key in configList.keys():
                for config in configList[key]:
                    myconfigIdx = configList[key].index(config)
                    #Check to see if all of the file Identifiers showed up in this line:
                    for fileID in config["fileIdentifiers"]:
                        # print "Checking identifier :" + fileID
                        # print "currLine: " + currLine
                        if fileID in currLine:
                            filescore[myconfigIdx] += 1
                            # print fileID + " is present, filescore: " + str(filescore)
                    # Reset column match score for every line and every config iteration
                    # check to see if all the fileCols from the config appear in the line:
                    colscore[myconfigIdx] = 0
                    for name in config["fileCols"]:
                        if name in currLine:
                            colscore[myconfigIdx] += 1
                    # If specific configuration matches file identifiers (filescore) and columns (colscore)
                    # then we found a match
                    if colscore[myconfigIdx] == len(config["fileCols"]) and \
                        filescore[myconfigIdx] == len(config["fileIdentifiers"]):
                        # print "match filescore: " + str(filescore[myconfigIdx])
                        # print "match colscore: " + str(colscore[myconfigIdx])
                        targetConfig = config
                        break
        currLine = fileObj.readline()

    # Reset the file to find the thread indexes
    # There appears to be multiple threads in some files, let's figure out where they are, then re-read the file:
    fileObj.seek(0,0)
    lineCount = 0
    currLine = fileObj.readline()
    while not currLine == "":
        lineCount+=1
        if not targetConfig == None:
            #Look for threadIndexes:
            if targetConfig["startMarker"][0] in currLine:
                threadIndexes.append(lineCount+targetConfig["startMarker"][1])
        currLine = fileObj.readline()
    #Reset the file & read from the new thread indexes
    fileObj.seek(0,0)
    # DEBUG: Start here to check which parser config is being used
    #print "DEBUG: GPTL parser config: " + str(targetConfig)
    #print "DEBUG: GPTL thread indexes: " + str(threadIndexes)
    return threadIndexes,targetConfig
    
def getData(src,configList = parserConfigs):
    #Check if src is a string, otherwise attempt to read from a file object:
    sourceFile=None
    if type(src) == types.StringType:
        sourceFile = open(src,"r")
    else:
        sourceFile = src
    lineCount = 0
    resultLines=[]

    threadIndexes,fileConfig = detectMtFile(sourceFile,configList)

    for line in threadIndexes:
        resultLines.append([])
        firstItr = True
        while True:
            lineCount+=1
            currLine = sourceFile.readline()
            if lineCount >= line:
                if countSpaces(currLine) == 0 and currLine=="\n": #This is true when we run out of needed data.
                    break
                #this became a little meta, so here's a reference in order to continue indexing:
                thread = resultLines[len(resultLines)-1]
                if countSpaces(currLine) == fileConfig["rootParent"] or firstItr:
                    thread.append([])
                    firstItr = False
                thread[len(thread)-1].append(str(currLine) )

    sourceFile.close()
    return resultLines,fileConfig

#In theory, this should get used quite a bit, despite being simple...
def countSpaces(strInput):
    count=0
    if not strInput == "":
        while strInput[count] in [" ","*"]:
            count+=1
    return count

#Recursive function that looks at one line, and checks to see if that line has children. (which in turn re-runs the function)
def parseNode(lineInput,config,currLine=0,parent=None):
    resultNode = timeNode()
    if parent:
        resultNode.parent = parent
    #Parse information from the line:
    #Look for the element that has quotation marks in it:
    foundQuotes = True
    nameSearch = []
    if '"' not in lineInput[currLine]:
        foundQuotes = False
        nsMarkerSplit = lineInput[currLine].split(" ")
        marker = ""
        for markerWord in nsMarkerSplit:
            if not markerWord == "" and not markerWord == "*":
                marker = markerWord
                break
        nameSearch = lineInput[currLine].split(marker,1)
        resultNode.name = marker.replace('"',"")
    else:
        nameSearch = lineInput[currLine].split('"',2)
    for word in nameSearch:
        if len(word) > 0:
            if word[0] not in ["*"," "] and foundQuotes:
                resultNode.name = word
                break
            elif word[0] == "*":
                resultNode.multiParent = True
                if not foundQuotes:
                    break

    elements=nameSearch[len(nameSearch)-1].split(" ")
    valueCount=0
    for wordCheck in elements:
        word = wordCheck.strip("()\n")
        if word not in ["","\n"]:
            if word not in ["-","y"]:
                resultNode.values[config["outCols"][valueCount]] = float(word.strip(')\n')) #The logic gate above fails to catch parenthesis with newlines, so this is here XP
                valueCount+=1
            else:
                tf = False
                if word == 'y':
                    tf=True
                resultNode.values[config["outCols"][valueCount]] = tf
                valueCount+=1
    #Try to find children until the indentation in the file no longer matches a child
    parentSpaceCount = countSpaces(lineInput[currLine])
    childrenIndex = currLine+1
    if currLine < (len(lineInput)-1):
        while countSpaces(lineInput[childrenIndex]) > parentSpaceCount:
            if countSpaces(lineInput[childrenIndex]) == parentSpaceCount+config["rootParent"]:
                childNode = parseNode(lineInput,config,childrenIndex,resultNode)
                resultNode.children.append(childNode)
            childrenIndex+=1
            if childrenIndex > len(lineInput)-1:
                break
    return resultNode

#When reading threads from a file, the returned list goes down to three dimensions! This "meta function" is to help with those headaches.
#This function assumes you're inserting thread(s) from getData()
def parseThread(thread,config):
    if len(thread) == 0:
        return []
    elif type(thread[0][0]) == types.StringType:
        resultNodes = []
        for nodes in thread:
            resultNodes.append(parseNode(nodes,config))
        return resultNodes
    elif type(thread[0][0]) == types.ListType:
        resultThreads=[]
        for element in thread:
            resultThreads.append(parseThread(element,config))
        return resultThreads

def typeResolver(mtObj):
    """This function is designed to bridge the gap between parsed JSON and mt classes. It shouldn't need to be used often, but if you don't know what your input will be, just use this.
    
    The function returns a dictionary of values that come from either timeNode objects, or json files.
    """
    output = {"name":None,"values":None,"children":None}
    if type(mtObj) == types.DictType:
            output["name"] = mtObj["name"]
            output["children"] = mtObj["children"]
            output["values"] = mtObj["values"]
    else:
        output["name"] = mtObj.name
        output["children"] = mtObj.children
        output["values"] = mtObj.values
    return output

#Return a node with the first instance of the requested name; this function only works with parsed nodes.
def searchNode(nodeIn,name):
    #A little tweak to make things compatible with lists...
    nodeList = []
    if type(nodeIn) == types.ListType:
        nodeList = nodeIn
    else:
        nodeList.append(nodeIn)

    for node in nodeList:
        #Check if the very node we're on is the one being searched for:
        if typeResolver(node)["name"] == name:
            return node
        else:
            #Check if each child has the correct name:
            for child in typeResolver(node)["children"]:
                resolveDict = typeResolver(child)
                if resolveDict["name"] == name:
                    return child
                elif len(resolveDict["children"]) > 0:
                    searchedNode = searchNode(child,name)
                    if typeResolver(searchedNode)["name"] == name:
                        return searchedNode
    return nodeIn

#Recursively convert your nodes into JSON.
def toJson(nodeIn,useBrackets=True):
    resultString=''
    if type(nodeIn) == types.ListType:
        if len(nodeIn) > 0 and type(nodeIn[0]) == types.ListType:
            #Aha! we have a multi-threaded collection:
            for i in range(len(nodeIn)):
                resultString+=toJson(nodeIn[i])
                if i < len(nodeIn)-1:
                    resultString+=','
        else:
            for i in range(len(nodeIn)):
                resultString+=toJson(nodeIn[i],False)
                if i < len(nodeIn)-1:
                    resultString+=','
    else:
        resultString='{"name":"'+nodeIn.name+'","multiParent":'+json.dumps(nodeIn.multiParent)+',"values":'+json.dumps(nodeIn.values)+',"children":'+toJson(nodeIn.children)+'}'
    if useBrackets:
        resultString = "["+ resultString +"]"
    return resultString

#The cherry on top: All functions above are called, and a complete JSON output is returned from all the layers of obscurity.
#In case you want pre-json output, returnLayer lets you stop the compilation process at any moment and return the current output. Besides JSON, the end result will always be stored in a list
def parse(fileIn,configList = parserConfigs,returnLayer=2):
    nodeLines,config = getData(fileIn,configList)
    if returnLayer == 0:
        return nodeLines
    resultThreads = parseThread(nodeLines,config)
    # print "Debug: parse thread done"
    if returnLayer == 1:
        return resultThreads
    return toJson(resultThreads)

