#Author: Zachary Mitchell
#Purpose: transfer timeNode objects from "modelTiming.py" into a database using sqlAlchemy.

import sqlalchemy
from sqlalchemy import create_engine,Table,Column,Integer,String,MetaData,ForeignKey
from modelTiming import valueList,timeNode

#Initialize the database for use with this algorhythm.
def makeTables(address):
    engine  = create_engine(address)
    metadata = MetaData()
    return

def write(tNodeSet,address,mainProcess=True,parentId=None,ltInfo={"id":0,"childId":0,"columns":[]}):
    #ltInfo is a way to directly address certain values as this algorhythm recurses.
    for node in tNodeSet:
        if mainProcess:
            ltInfo["childId"] = 0
        ltInfo["columns"].append({"name":node.name,"wallClock":node.values["wallClock"],"parentId":parentId,"id":ltInfo["id"],"childId":ltInfo["childId"]})
        #Grab any values that this node contains:
        for key in node.values.keys():
            ltInfo["columns"][len(ltInfo["columns"])-1][key] = node.values[key]
        #print(ltInfo["columns"][len(ltInfo["columns"])-1])
        ltInfo["id"]+=1
        ltInfo["childId"]+=1
        if len(node.children) > 0:
            write(node.children,address,False,ltInfo["childId"]-1,ltInfo)
    if mainProcess:
        return ltInfo["columns"]

#Returns a set of timeNodes imported from your db.
def read(address,columns=[]):
    splitCols=[]
    resultNodes=[]
    #Query for the experiment:

    #(code here)

    #Split the results down for every childId of 0:
    for item in columns:
        if item["childId"] == 0:
            splitCols.append([])
        splitCols[len(splitCols)-1].append(item)
    print(len(splitCols))
    #Ok, let's go through each item, and create timeNodes based on the columns:
    for process in splitCols:
        #Create the nodes:
        processNodes = []
        for subprocess in process:
            newNode = timeNode()
            newNode.name=subprocess["name"]
            processNodes.append(newNode)
        #Link all the timeNodes together based on parentId; this should become one big processes:
        for i in range(len(process)):
            if not process[i]["parentId"] == None:
                #Initialize values:
                processNodes[process[i]["parentId"]].children.append(processNodes[i])
                processNodes[i].parent = processNodes[process[i]["parentId"]]
            elif process[i]["childId"] == 0:
                processNodes[i].parent = processNodes[i]
            #Grab elements only if they exist as a timeNode value:
            for key in process[i].keys():
                if key in valueList[0] or key in valueList[1]:
                    processNodes[i].values[key] = process[i][key]

        resultNodes.append(processNodes[0])
    return resultNodes