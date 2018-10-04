#Author: Zachary Mitchell
#Purpose: Parse the top of README.case.* files. The parsed object represents an excutable with arguments
import types
def parse(fileIn):
    resultElement = {}
    commandLine = None
    #This should support file objects if one's inserted:
    if type(fileIn) == types.StringType:
        commandLine = open(fileIn).readline()
    else:
        commandLine = fileIn.readline()
    cmdArgs = commandLine.split(": ",1)[1].strip("./\n").split(" ")
    resultElement["name"] = cmdArgs[0]
    for i in range(len(cmdArgs)):
        if cmdArgs[i][0] == "-":
            if "=" in cmdArgs[i]:
                argumentStr = cmdArgs[i].strip("-").split("=")
                resultElement[argumentStr[0]] = argumentStr[1]
            else:
                argument = cmdArgs[i].strip("-")
                resultElement[argument] = cmdArgs[i+1]
    resultElement["date"] = commandLine.split(": ",1)[0].strip(":")
    return resultElement