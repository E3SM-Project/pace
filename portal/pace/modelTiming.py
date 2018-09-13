#Author: Zachary Mitchell
#Purpose: parse files that come from GPTL (https://jmrosinski.github.io/GPTL/) to create a programatic representation of the output.
import types,json
valueList=[
    ["on","called","recurse","wallClock","max","min","utrOverhead"],
    ["processes","threads","count","walltotal","wallmax","wallmax_proc","wallmax_thrd","wallmin","wallmin_proc","wallmin_thrd"]
]
class timeNode(object):
    #Without this, a reeealy weird scoping problem happens; not sure why.
    def __init__(self):
        self.name="default"
        self.multiParent = False
        self.values={}
        self.children=[]
        self.parent = self #Should this refer to itself... or have none?

def getData(src):
    #Check if src is a string, otherwise attempt to read from a file object:
    sourceFile=None
    isStat=False #if this is a model_timing_*_stats file, this will be flicked on.
    if type(src) == types.StringType:
        sourceFile = open(src,"r")
    else:
        sourceFile = src
    lineCount = 0
    resultLines=[]
    threadIndexes=[]
    currLine = ""
    #There appears to be multiple threads in some files, let's figure out where they are, then re-read the file:
    currLine = sourceFile.readline()
    while not currLine == "":
        if "Stats for thread" in currLine:
            threadIndexes.append(lineCount+3)
        elif "GLOBAL STATISTICS" in currLine:
            isStat=True #we found a statistics file instead of a regular file.
        lineCount+=1
        if isStat and "name" in currLine:
            threadIndexes.append(lineCount+1)
        currLine = sourceFile.readline()
    #Reset the file & read from the new thread indexes
    sourceFile.seek(0,0)
    lineCount=0

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
                if countSpaces(currLine) == 2 or isStat or firstItr:
                    thread.append([])
                    firstItr = False
                thread[len(thread)-1].append(str(currLine) )

    sourceFile.close()
    return resultLines

#In theory, this should get used quite a bit, despite being simple...
def countSpaces(strInput):
    count=0
    if not strInput == "":
        while strInput[count] in [" ","*"]:
            count+=1
    return count

#Recursive function that looks at one line, and checks to see if that line has children. (which in turn re-runs the function)
def parseNode(lineInput,currLine=0,parent=None):
    vlIndex=0
    if "(" in lineInput[currLine]:
        vlIndex=1
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
        word = wordCheck.strip("()")
        if word not in ["","\n"]:
            if word not in ["-","y"]:
                resultNode.values[valueList[vlIndex][valueCount]] = float(word.strip(')\n')) #The logic gate above fails to catch parenthesis with newlines, so this is here XP
                valueCount+=1
            else:
                tf = False
                if word == 'y':
                    tf=True
                resultNode.values[valueList[vlIndex][valueCount]] = tf
                valueCount+=1
    #Try to find children until the indentation in the file no longer matches a child
    parentSpaceCount = countSpaces(lineInput[currLine])
    childrenIndex = currLine+1
    if currLine < (len(lineInput)-1):
        while countSpaces(lineInput[childrenIndex]) > parentSpaceCount:
            if countSpaces(lineInput[childrenIndex]) == parentSpaceCount+2:
                childNode = parseNode(lineInput,childrenIndex,resultNode)
                resultNode.children.append(childNode)
            childrenIndex+=1
            if childrenIndex > len(lineInput)-1:
                break
    return resultNode

#When reading threads from a file, the returned list goes down to three dimensions! This "meta function" is to help with those headaches.
#This function assumes you're inserting thread(s) from getData()
def parseThread(thread):
    if len(thread) == 0:
        return []
    elif type(thread[0][0]) == types.StringType:
        resultNodes = []
        for nodes in thread:
            resultNodes.append(parseNode(nodes))
        return resultNodes
    elif type(thread[0][0]) == types.ListType:
        resultThreads=[]
        for element in thread:
            resultThreads.append(parseThread(element))
        return resultThreads

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
        if node.name == name:
            return node
        else:
            #Check if each child has the correct name:
            for child in node.children:
                if child.name == name:
                    return child
                elif len(child.children) > 0:
                    searchedNode = searchNode(child,name)
                    if searchedNode.name == name:
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
def parse(fileIn,returnLayer=2):
    nodeLines = getData(fileIn)
    if returnLayer == 0:
        return nodeLines
    resultThreads = parseThread(nodeLines)
    if returnLayer == 1:
        return resultThreads
    return toJson(resultThreads)