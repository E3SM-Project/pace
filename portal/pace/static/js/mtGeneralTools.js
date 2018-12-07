//Author: Zachary Mitchell
//Purpose: This file is here in the event where more than one tool could come in handy for the modelTiming json format

//This will be where we look for a specific node. (Making the structured time-node into something linear at the same time)
function addressTable(vals=undefined,jsonArray=false,srcExp,thread = -1){
    let newAddressTable = [];
    //It appears that all names for nodes are unique! Let's make use of that...
    newAddressTable.addVals = function(jsonIn,jsonArray = false,parent=undefined){
        if(jsonArray){
            jsonIn.forEach(element=>this.addVals(element));
        }
        else{
            //The awesomness of Javascript allows us to iterate AND call objects by name
            this[jsonIn.name] = jsonIn;
            this.push(jsonIn);
            jsonIn.children.forEach(child=>this.addVals(child,false,jsonIn));
            //Making Parents...
            this[jsonIn.name].parent=(parent==undefined?jsonIn:parent);
            this[jsonIn.name].srcExp = srcExp;
            this[jsonIn.name].thread = thread;
        }
    }
    if(vals)
    newAddressTable.addVals(vals,jsonArray)
    
    newAddressTable.noChildren = true;
    for(let i=0;i<newAddressTable.length;i++){
        if(newAddressTable[i].children.length > 0){
            newAddressTable.noChildren = false;
            break;
        }
    }
    return newAddressTable
}