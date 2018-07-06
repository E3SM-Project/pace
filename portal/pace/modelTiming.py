#Author: Zachary Mitchell
"""Purpose: parse files that come from GPTL (https://jmrosinski.github.io/GPTL/)
to create a programatic representation of the output.
"""
import types,json
valueList=["on","called","recurse","wallClock","max","min","utrOverhead"]

class timeNode(object):
    #Without this, a reeealy weird scoping problem happens; not sure why.
    def __init__(self):
        self.name="default"
        self.multiParent = False
        self.values={}
        self.children=[]
        self.parent = self #Should this refer to itself... or have none?

def getData(src,startLine=24):
    #Check if src is a string, otherwise attempt to read from a file object:
    sourceFile=None
    if type(src) == types.StringType:
        sourceFile = open(src,"r")
    else:
        sourceFile = src
    lineCount = 0
    resultLines=[]
    currLine = sourceFile.readline()
    while not currLine == "":
        lineCount+=1
        if lineCount >= startLine:
            currLine = sourceFile.readline()
            if countSpaces(currLine) == 0: #This seems to work over comparing it to "" :/ [Oddly enough, the function does the exact same thing when handling "" ...weird]
                break
            elif countSpaces(currLine) == 2:
                resultLines.append([])
            resultLines[len(resultLines)-1].append(currLine)
        else:
            sourceFile.readline()
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
    resultNode = timeNode()
    if parent:
        resultNode.parent = parent
    #Parse information from the line:
    #Look for the element that has quotation marks in it:
    nameSearch = lineInput[currLine].split('"',2)
    for word in nameSearch:
        if word[0] not in [" ","","*"]:
            resultNode.name=word
            break
        elif word[0] == "*":
            resultNode.multiParent = True

    elements=nameSearch[len(nameSearch)-1].split(" ")
    valueCount=0
    for word in elements:
        if word not in ["","\n"]:
            if word not in ["-","y"]:
                #print "\n'"+word+"'\n"
                resultNode.values[valueList[valueCount]] = float(word)
                valueCount+=1
            else:
                tf = False
                if word == 'y':
                    tf=True
                resultNode.values[valueList[valueCount]] = tf
                valueCount+=1
    #Try to find children until the indentation in the file no longer matches a child
    parentSpaceCount = countSpaces(lineInput[currLine])
    childrenIndex = currLine+1
    #print(str(currLine < len(lineInput)-1)+" | currLine:"+str(currLine)+" | lineInput:"+str(len(lineInput)-1))
    if currLine < (len(lineInput)-1):
        while countSpaces(lineInput[childrenIndex]) > parentSpaceCount:
            if countSpaces(lineInput[childrenIndex]) == parentSpaceCount+2:
                childNode = parseNode(lineInput,childrenIndex,resultNode)
                #print ("Child: "+str(childNode))
                #print(resultNode.name+"(after): "+str(resultNode.values['wallClock']))
                resultNode.children.append(childNode)
            childrenIndex+=1
            if childrenIndex > len(lineInput)-1:
                break
    return resultNode

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
        for i in range(len(nodeIn)):
            resultString+=toJson(nodeIn[i],False)
            if i < len(nodeIn)-1:
                resultString+=','
    else:
        resultString='{"name":"'+nodeIn.name+'","multiParent":'+json.dumps(nodeIn.multiParent)+',"values":'+json.dumps(nodeIn.values)+',"children":'+toJson(nodeIn.children)+'}'
    if useBrackets:
        resultString = "["+ resultString +"]"
    return resultString