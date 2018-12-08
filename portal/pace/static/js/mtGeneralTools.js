//Author: Zachary Mitchell
//Purpose: This file is here in the event where more than one tool could come in handy for the modelTiming json format

var isChrome = /Chrome/.test(navigator.appVersion);

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

/*There's a bug (either in google chrome or in this metaOpenClose) that stretches the metatable after closing it.
I'm guessing this is a chrome bug, since the debugger doesn't show values being changed in any way. The below function fixes this issue.*/
function metaContainerChromeFix(){
    if(isChrome && metaTable.style.display == "none"){
        metaInfoContainer.style.display="none";
        setTimeout(()=>metaInfoContainer.style.display="inline",10);
    }
}

//Open and close the meta-info box
function metaOpenClose(openClose=false,metaArray){
    if(metaArray){
        let outStr=""
        if(metaArray.length > 1){
            outStr = `<span onclick='$(metaTable).slideToggle(200,metaContainerChromeFix)' style='cursor:pointer'>Click to view more details about these experiments.</span>
            <div id='metaTable' style="display:none;text-align:left;margin-left:25%"><table><thead><tr><th>Compset</th><th>Res</th><th>Expid</th></tr></thead><tbody>`;
            metaArray.forEach(exp=>{
                outStr+="<tr><td>"+exp.compset+"</td><td>"+exp.res+"</td><td><a href='"+detectRootUrl()+"exp-details/"+exp.name+"'>"+exp.name+"</a></td></tr></div>";
            });
            outStr+="</tbody></table>"
        }
        else{
            outStr = "Compset: <a href='"+detectRootUrl()+"advsearch/compset:"+metaArray[0].compset+"'>"+metaArray[0].compset+"</a> Res: <a href='"+detectRootUrl()+"advsearch/res:"+metaArray[0].res+"'>"+metaArray[0].res+"</a> (<a href='"+detectRootUrl()+"exp-details/"+metaArray[0].name+"'>Details</a>)";
        }
        $(metaInfoContainer).slideUp(200);
        metaInfoTxt = metaInfoContainer.children[0];
        setTimeout(()=>metaInfoTxt.innerHTML = outStr,metaInfoTxt.innerHTML == ""?0:200);
        $(metaInfoContainer).slideDown(200);
    }
    if(openClose)
        $(metaInfoContainer).slideDown(200);
    else
        $(metaInfoContainer).slideUp(200);
}