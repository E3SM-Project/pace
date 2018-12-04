#Author: Zachary Mitchell
#Purpose: Create a new pacerc file. This either generates one, or grabs a "file" from the arguments.
#This is designed to be used in docker where you can't send files through standard input, but it can also be used standalone.
import sys
import ConfigParser
#The values in the rc file. the first index in each array is an alternate name, and the second is the name of the value.
#These can be changed out for any other values one might want
rcValues = {
    "PACE":["username","password","db","host"],
    "MINIO":["minio_access_key","minio_secret_key","minio_url"],
    "GITHUBAPP":["githubapp_client_id","github_secret_key"]
}

usrRcVals = ConfigParser.RawConfigParser()
usrRcVals.add_section("PACE")
usrRcVals.add_section("MINIO")

#the rc values in string format:
rcValStr = ""
for key in rcValues.keys():
    rcValStr+="=="+key+"==\n"
    for element in rcValues[key]:
        rcValStr+= element+"\n"

usage = "Usage: "+sys.argv[0]+" arg1 arg1 [etc...] OR "+sys.argv[0]+" var1=value1 var2 = value2 etc=etc"+"""

Create a new rc file for PACE (as of this writing). It can be used standalone, or as part of dockerExec.sh (original intent)
Variables can be simply typed straight from arguments, or have associated variable names with them (e.g var=value), but only one method can be used per command call.

The result is printed to stdout, so to save this config, the user would do the following in bash: """+sys.argv[0]+""" [args] >> /path/to/rcFile

List of variables:

"""+rcValStr

printResults = False
equalPoints = 0 #This stores who many equal signs were detected
if len(sys.argv) > 1 and sys.argv[1] in ["-h","--help"]:
    print(usage)
    exit()
else:
    #Scan arguments:
    for arg in sys.argv:
        if not arg == sys.argv[0] and "=" in arg:
            equalPoints+=1

if equalPoints > 0:
    printResults = True
    #Check to see if everything either matches a keyword, aor a shortcut word:
    #Sorry... This is a lot of for loops >_<
    for i in range(len(sys.argv)):
        if i > 0:
            for category in rcValues.keys():
                for element in rcValues[category]:
                    targetStr = sys.argv[i].split("=")
                    if targetStr[0] == element:
                        usrRcVals.set(category,element, targetStr[1])
                        break
elif equalPoints == 0 and len(sys.argv) > 1:
    printResults = True
    #Go through each argument and add them to the config until we run out.
    currArgIndex = 1
    for key in rcValues.keys():
        for element in rcValues[key]:
            if not currArgIndex == len(sys.argv):
                usrRcVals.set(key,element,sys.argv[currArgIndex])
                currArgIndex+=1
            else:
                break
#Print everything to stdout:
if printResults:
    with sys.stdout as console:
        usrRcVals.write(console)
else:
    print(usage)