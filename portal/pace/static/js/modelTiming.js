//Author: Zachary Mitchell
//Purpose: These are the core functions for displaying everything in modelTiming.html

var okToClick=true;
var stackedCharts = true;
var currExp;
var expList = [];

//A backlog of things to do when all experiments are retrieved. It is cleared out afterwards.
var expGetCount = 0;
var expGetFunc = [];

//The default color configuration, setting this to undefined will make the mtViewer use the defaults in percentToColor()
var colorConfig = [];
var colorSetting = -1;
var smoothColors = false;

//Address table has been moved to mtGeneralTools.js

//This holds a single experiment. The goal is to be able to compare multiples, so they are compartmentelized here.
function experiment(timeNodes,config){
    this.timeNodes = timeNodes;
    //Whichever node is selected, everything in the code will follow this index for appropriate addressing:
    this.currThread = 0;
    //Whichever node is currently selected, it will appear here.
    this.currentEntry=undefined;
    //We have multiple threads to show off; let's cilo these so we can load then up on the fly:
    this.nodeTableList = [];
    this.nodeDomList = [];
    this.threadSelectInner = "";
    this.valueSelectInner = this.rank == "stats"?"<option value='wallmin/wallmax'>wallMin / wallMax</option>":"<option value='nodes'>processes</option><option value='min/max'>Min / Max</option>";

    let defaultConfig = {
        name:"Unnamed Experiment",
        rank:"0",
        compset:"N/A",
        res:"N/A",
        valueNames:undefined
    };
    //Make sure we have everything based on the config argument, if not, it's set to default:
    Object.keys(defaultConfig).forEach(key=>{
        this[key] = config[key]?config[key]:defaultConfig[key];
    });

    //Construct:
    this.timeNodes.forEach((thread,i)=>{
        this.nodeTableList.push(addressTable(thread,true,this,i));
        this.nodeDomList.push(htmlList(thread,[0,2]));
        this.threadSelectInner+="<option "+ (!i?"selected":"")+" value="+i+" >Thread "+i+"</option>";
    });
    //It should be safe to assume that all value names are the same; if not, this can be easily changed to reflect each thread.
    if(this.valueNames==undefined)
        this.valueNames = Object.keys(this.nodeTableList[0][0].values);
    this.valueNames.forEach(name=>this.valueSelectInner+="<option "+(name=="wallClock" || name=="wallmax"?"selected":"")+" value='"+name+"'>"+name+"</option>");
    this.currentEntry = {children:this.timeNodes[this.currThread],name:"summaryButton"};

    this.view = function(){
        threadSelect.innerHTML = this.threadSelectInner;
        valueName.innerHTML = this.valueSelectInner;
        listContent.innerHTML = "";
        listContent.appendChild(this.nodeDomList[this.currThread]);
    }

}

function getExperiment(expSrc,extSrc,funcPush = expDownloadDefault){
    expGetCount++;
    if(funcPush)
        expGetFunc.push(funcPush);
    //jquery test
    $.get(detectRootUrl()+"summaryQuery/"+expSrc+"/"+extSrc+"/",function(data,status){
        if(status == "success"){
            let results = JSON.parse(data);
            //The name of the experiment will just be it's expid for now.
            results.meta.name=results.meta.expid;
            // console.log(results);
            expList.push(new experiment(results.obj,results.meta));
        }
        expGetCount--;
        if(expGetCount == 0){
            expGetFunc.forEach(element=>element());
            expGetFunc = [];
        }
    });
}
//this is the default function that's executed during an experiment download
function expDownloadDefault(){
    currExp = expList[expList.length-1];
    updateExpSelect();
    animate(false);
    currExp.view();
    metaOpenClose(true,[currExp]);
    mtViewer.closeDlList();
    //Construct a new url for browser display:
    let newUrl = detectRootUrl()+"summary/";
    let idStr = "";
    let rankStr = "";
    expList.forEach(exp=>{
        idStr+=(exp!=expList[0]?",":"")+exp.name;
        rankStr+=(exp!=expList[0]?",":"")+exp.rank;
    });
    history.pushState("","",newUrl+idStr+"/"+rankStr+(compare?"/compare/":"")+window.location.hash);
    if(window.location.hash=="" && !compare /*|| expList.length > 1*/)
        summaryButton.click();
    else
        //There's some lag when switching from regular mode to comparison mode when directly visiting a compare link, so this is here to let the chart render, *then change the hash.
        setTimeout(window.onhashchange,compare?10:0);
    expSelect.selectedIndex = expList.length-1;
    }

function switchExperiment(index = expSelect.selectedIndex){
    currExp = (typeof(index) == "object"?index:expList[index]);
    currExp.view();
    if(currExp.currentEntry == undefined)
        summaryButton.click();
    else mtViewer.loadChart();
    mtViewer.closeDlList();
    resultChart.options.title.text=currExp.name +": "+currExp.rank+ " (Thread "+currExp.currThread+")";
    metaOpenClose(true,[currExp]);

    let newUrl = detectRootUrl()+"summary/";
    let idStr = "";
    let rankStr = "";
    let firstExp = false;
    expList.forEach(exp=>{
        if(exp!=currExp){
            idStr+=(firstExp?",":"")+exp.name;
            rankStr+=(firstExp?",":"")+exp.rank;
            if(!firstExp)
                firstExp = true;
        }
    });
    idStr+=(idStr!=""?",":"")+currExp.name;
    rankStr+=(rankStr!=""?",":"")+currExp.rank;
    history.pushState("","",newUrl+idStr+"/"+rankStr+"#"+currExp.currentEntry.name);
}

//This creates an HTML list that directly associates with the address table (which in-turn addresses to the original json file). When a tag is clicked, the other lists witihin it are collapsed.
//scope is the range you want the subprocesses to be closed by default. (e.g a range of 0-2 would have the rest of the nodes opened by default by the 3rd layer.)
function htmlList(jsonList,scope=[0,0],currScope=0){
    let newList = document.createElement("ul");
    //Add colors to each element on the list as long as it contains children:
    let sumList = [];
    jsonList.forEach(child=>sumList.push(mtSum(child)[1]));
    let percentList=arrayToPercentages(sumList);
    let percentIndex=0;
    //List of nodes go inside...
    jsonList.forEach((node)=>{
        let listElement = document.createElement("li");
        listElement.id=node.name;
        listElement.innerHTML+="<span>"+node.name+"</span>";
        listElement.onclick = Function("htmlList_onClick(this)");

        //Make more lists:
        if(node.children.length>0){
            listElement.appendChild(htmlList(node.children,scope,currScope+1));
            listElement.getElementsByTagName("span")[0].style.backgroundColor=percentToColor(percentList[percentIndex],.4,0,colorConfig);
            if(currScope >= scope[0] && currScope<=scope[1])
                listElement.getElementsByTagName("ul")[0].style.display="none";
        }
        newList.appendChild(listElement);
        percentIndex++;
    });

    return newList;
}

//This is reserved for an htmlList element. It's here so that functions arn't called on the spot and take up more memory.
function htmlList_onClick(context){
    targetExp = mtViewer.currExp();
    if(targetExp.currentEntry!=undefined && targetExp.currentEntry.name == context.id && targetExp.nodeTableList[targetExp.currThread][context.id].children.length > 0){
        let listTag = context.getElementsByTagName("ul")[0].style;
        listTag.display=(listTag.display=="none"?"":"none");
        //Pretty much stops all other clicks from triggering.
        okToClick = false;
        //Change the url; this would normaly be recursive, but thanks to okToClick, that can all be prevented!
        history.replaceState("","",window.location.href.split("#")[0]+"#"+context.id);
        setTimeout(()=>okToClick = true,10);
    }
    else if(okToClick){
        if (targetExp.currentEntry == undefined || targetExp.currentEntry.name!= context.id){
            context.style.fontWeight="bold";
            if(targetExp.currentEntry !=undefined && targetExp.currentEntry.name !=undefined)
                document.getElementById(targetExp.currentEntry.name).style.fontWeight="";
            targetExp.currentEntry = targetExp.nodeTableList[targetExp.currThread][context.id];
        }
        okToClick = false;
        history.replaceState("","",window.location.href.split("#")[0]+"#"+context.id);
        setTimeout(()=>okToClick = true,10);

        mtViewer.loadChart(context.id);
    }
}

//This handles the makeGraphBar function to change the graph as a whole.
function changeGraph(nodeIn,valIn=valueName.children[valueName.selectedIndex].value,stackedBar = stackedCharts){
    resultChart.data.labels=[];
    //This is the easiest way to clear out multi-bar data...
    resultChart.data.datasets = [];
        if(valIn=="min/max" || valIn == "wallmin/wallmax"){
            minmaxIndex = 0;
            minmaxArray = [
                ["min","max"],
                ["wallmin","wallmax"]
            ];
            if(valIn == "wallmin/wallmax")
                minmaxIndex++;
            for(let i=0;i<nodeIn.children.length;i++){
                resultChart.data.labels.push(nodeIn.children[i].name);
                minmaxArray[minmaxIndex].forEach((minMax,index)=>makeGraphBar({children:[nodeIn.children[i]]},minMax,i,index));
            }
            resultChart.data.datasets[0].label=minmaxArray[minmaxIndex][0];
            resultChart.data.datasets[1].label=minmaxArray[minmaxIndex][1];
        }
        else{
            //First,lets check to see if everything has no children, that way, we can turn stackedBar off if needed:
            let noChildCheck=0;
            for(let i=0;i<nodeIn.children.length;i++){
                if(nodeIn.children[i].children.length == 0)
                    noChildCheck++;
            }
            if(noChildCheck == nodeIn.children.length)
                stackedBar=false;
            for(let i=0;i<nodeIn.children.length;i++){
                resultChart.data.labels.push(nodeIn.children[i].name);
                makeGraphBar( (stackedBar?nodeIn.children[i]:{children:[nodeIn.children[i]]} ),valIn,i);
            }
        }
    colorChart(colorSetting);
    resizeChart();
    //This is to help fix a bug in chartjs & resizing the chart
    if(chartTag.height*1 <chartTag.style.height.replace("px","")*1)
        setTimeout(resizeChart,10);
    resultChart.update();
}

//Creates a row of information based on the selected index.
function makeGraphBar(nodeIn,valIn="nodes",dataIndex=0,stackOffset=0){
    // console.log(nodeIn.children);
    //Get all the children in this node:
    let mtData = [];//Data from mtSum
    //Instead of using the recursive sum, it has been changed so that the face-value of a child is printed:
    nodeIn.children.forEach(child=>mtData.push( valIn == "nodes"?mtSum(child):[child.values[valIn],mtSum(child)[1]] ));

    let offset = nodeIn.children.length * stackOffset;

    //create new datasets if they don't exhist
    for(let i=0;i<mtData.length;i++){
        if(resultChart.data.datasets[i+offset] == undefined)
            resultChart.data.datasets[i+offset] = {
                borderWidth:1,
                data:[],
                backgroundColor:[],
                borderColor:[]};
    }

    //Take it to chartData based on mode:
    switch(mode.children[mode.selectedIndex].value){
        case "sum":
        let displayIndex = (valIn == "nodes"?1:0);
        for(let i=0;i<mtData.length;i++){
            resultChart.data.datasets[i+offset].data[dataIndex]=mtData[i][displayIndex];
        }
        break;
        case "avg":
        for(let i=0;i<mtData.length;i++){
            resultChart.data.datasets[i+offset].data[dataIndex]=(mtData[i][0] / mtData[i][1]);
        }
        break;
    }
}

//Chart coloring is handled here so resultChart isn't colored more than once:
function colorChart(mode=-1,colorList = colorConfig,smoothTransition = smoothColors){
    //Clear the current colors:
    resultChart.data.datasets.forEach(e=>{
        e.backgroundColor=[];
        e.borderColor=[];
    });

    if(mode == -1){
        //Automatically choose an option:

        //Check for no children (roughly the same algorhythm from changeGraph):
        let noChildren = true;
        if(mtViewer.currExp().currentEntry.children.length == 0)
            noChildren = false;
        else for(let i=0;i<mtViewer.currExp().currentEntry.children.length;i++){
            if(mtViewer.currExp().currentEntry.children[i].children.length > 0){
                noChildren = false;
                break;
            }
        }
        if(comparisonMode.on) mode = 2;
        else if(noChildren || !stackedCharts) mode = 0;
        else if (stackedCharts) mode = 1
    }

    switch(mode){
        case 0:
            //Color based on all data on the chart:
            let colorSumlist = [];
            // for(let j=0;j<resultChart.data.datasets[0].data.length;j++)
            //     colorSumlist.push(resultChart.data.datasets[0].data[j]);
            let targetValue = valueName.children[valueName.selectedIndex].value;
            if(mtViewer.currExp().currentEntry.children.length > 0)
                mtViewer.currExp().currentEntry.children.forEach(e=>colorSumlist.push(targetValue == "nodes"?mtSum(e)[1]:e.values[targetValue]));
            else colorSumlist.push(targetValue == "nodes"?mtSum(mtViewer.currExp().currentEntry)[1]:mtViewer.currExp().currentEntry.values[targetValue]);
            
            //color everything the same color in one dataset:
            let colorPercentages = arrayToPercentages(colorSumlist);
            for(let i=0;i<resultChart.data.datasets.length;i++){
                for(let j=0;j<resultChart.data.datasets[i].data.length;j++){
                    let colorData = percentToColor(colorPercentages[j],.4,2,colorList,smoothTransition);
                    resultChart.data.datasets[i].backgroundColor.push(colorData[0]);
                    resultChart.data.datasets[i].borderColor.push(percentToColor(50,.4,0,[colorData[1],[0,0,0]]));
                }
            }
        break;
        case 1:
            //Color each stacked bar individually:
            for(let i=0;i<resultChart.data.datasets[0].data.length;i++){
                let colorSumlist = [];
                for(let j=0;j<resultChart.data.datasets.length;j++)
                    colorSumlist.push(resultChart.data.datasets[j].data[i]);
                let colorPercentages = arrayToPercentages(colorSumlist);
                for(let j=0;j<resultChart.data.datasets.length;j++){
                    let colorData = percentToColor(colorPercentages[j],.4,2,colorList,smoothTransition);
                    resultChart.data.datasets[j].backgroundColor.push(colorData[0]);
                    resultChart.data.datasets[j].borderColor.push(percentToColor(50,.4,0,[colorData[1],[0,0,0]]));
                }
            }
        break;
        case 2:
            //Color each bar based on which experiment it came from:
            let valPool = [];
            if(mtViewer.currExp().currentEntry.children.length == 0){
                if(!valPool["e"+mtViewer.currExp().currentEntry.srcExp.name]){
                    //Here we create a frakenstine that acts like an associated array and a traditional one. This will help us properly address our percentages (Since an array is returned)
                    valPool["e"+mtViewer.currExp().currentEntry.srcExp.name] = {total:0,index:valPool.length};
                    valPool.push(valPool["e"+mtViewer.currExp().currentEntry.srcExp.name]);
                }
                valPool["e"+mtViewer.currExp().currentEntry.srcExp.name].total+=valPool["e"+mtViewer.currExp().currentEntry.srcExp.name].values[valueName.children[valueName.selectedIndex].value];
            }
            else mtViewer.currExp().currentEntry.children.forEach(child=>{
                    if(!valPool["e"+child.srcExp.name]){
                        //Ditto above:
                        valPool["e"+child.srcExp.name] = {total:0,index:valPool.length};
                        valPool.push(valPool["e"+child.srcExp.name]);
                    }
                    valPool["e"+child.srcExp.name].total += child.values[valueName.children[valueName.selectedIndex].value];
                });
            let resultPercentages = arrayToPercentages( (()=>{
                //This function creates an array that we only use once to generate percentages:
                resultArray = [];
                valPool.forEach(element=>resultArray.push(element));
                return resultArray;
            })(),true);
            //Now to actually color each bar:
            mtViewer.currExp().currentEntry.children.forEach((exp,index)=>{
                resultChart.data.datasets.forEach(dataSet=>{
                    let colorData = percentToColor(resultPercentages[valPool["e"+exp.srcExp.name].index],.4,2,colorList,smoothTransition);
                    dataSet.backgroundColor[index] = colorData[0];
                    dataSet.borderColor[index] = percentToColor(50,.4,0,[colorData[1],[0,0,0]]);
                });
            });
            
        break;
        case 3:
            //Color everything randomly:
            resultChart.data.datasets.forEach(dset=>{
                for(let i=0;i<dset.data.length;i++){
                    let rndColor = percentToColor(Math.floor(Math.random()*100),.4,2,colorList,smoothTransition);
                    dset.backgroundColor.push(rndColor[0]);
                    dset.borderColor.push(percentToColor(50,.4,0,[rndColor[1],[0,0,0]]));
                }
            });
    }
}

//Grabs the values needed from the timeNode tree(This is a direct port from what was used in modelTiming.py)
function mtSum(nodeIn,valName="nodes",parentNode=true){
    let total=0;
    let nodeCount=1;
    nodeIn.children.forEach(child=>{
        let output = mtSum(child,valName,false);
        total+=output[0];
        nodeCount+=output[1];
    });
    if (valName!="nodes")
        total+=nodeIn.values[valName];
    return [total,(parentNode?nodeCount-1:nodeCount)];
}

//Go backwards in a node to get a path from the parent to the child.
function parentPath(nodeIn,currValues=[]){
        currValues.push(nodeIn.name)
        if(nodeIn.name == nodeIn.parent.name)
            return currValues
        currValues = parentPath(nodeIn.parent,currValues);
        return currValues
}

//This object aims to unify common atributes between regular mode and comparison mode. So many methods for tying up both were littered across the code, so this should clean it up!
var mtViewer = {
    currExp:()=>comparisonMode.on?comparisonMode.exp:currExp,
    expList:()=>{
        if(comparisonMode.on){
            newExpList = [];
            activeExps.forEach(array=>{
                newExpList.push(array[0]);
            });
            return newExpList;
        }
        else return expList;
    },
    loadChart:function(processId = mtViewer.currExp().currentEntry.name){
        targetExp = this.currExp();
        //Display appropriate graph info:
        if(processId == "summaryButton")
            summaryButton.click();
        else if(targetExp.nodeTableList[targetExp.currThread][processId].children.length > 0){
            resultChart.options.title.text=processId;
            if(comparisonMode.on)
                setTimeout(()=>comparisonMode.viewChart(processId),10);
            //Strange... there's a small chance that something asynchronous will take too long before chart.js can render the chart... LET'S FIX THAT!
            else setTimeout(()=>changeGraph(currExp.nodeTableList[currExp.currThread][processId]),10);
        }
        else{
            if(comparisonMode.on)
                setTimeout(()=>comparisonMode.viewChart(processId),10);
            else setTimeout(()=>changeGraph({children:[currExp.nodeTableList[currExp.currThread][processId]]}),10);
        }
    },
    //If the data list has no children, close it. If it's not mobile, there's a chance somebody would use the data list...
    closeDlList:()=>{
        if(currExp.nodeTableList[currExp.currThread].noChildren)
            dlSlide(dlShow = false);
        else if(window.innerWidth > 700)
            dlSlide(dlShow = true);
    }
}

var comparisonMode = {
    on:false,
    exp:undefined,
    relatedNodes:[],
    activeExps:[],
    activeChildren:[],
    new:function(expList){
        //As long as values are the same, we can run this function:
        let valBenchmark = expList[0][0].valueNames;
        let sameVals = true;
        expList.forEach(element=>{
            for(let i=0;i<valBenchmark.length;i++){
                let found = false;
                for(let j=0;j<element[0].valueNames.length;j++){
                    if(element[0].valueNames[j] == valBenchmark[i])
                        found = true;
                }
                if(!found){
                    sameVals = false;
                    break;
                }
            }
        });
        if(sameVals){
            let timeNodeList = [];
            expList.forEach(exp=>timeNodeList.push(exp[0].timeNodes[exp[1]]));
            let relNodeTemp = this.genList(timeNodeList,true);
            this.relatedNodes = [];
            relNodeTemp.forEach(element=>this.relatedNodes.push(expList[element]));
            let compareName = "Comparison: ";
            let firstStr = true;
            this.relatedNodes.forEach(exp=>{
                compareName+=(firstStr?"":",")+exp[0].name+"_"+exp[0].rank+"(thread "+exp[1]+")";
                firstStr = false;
            })
            this.exp = new experiment([this.genList(timeNodeList)],{
                name:compareName,
                rank:(expList[0][0].rank == "stats"?"stats":"0"),
                valueNames:expList[0][0].valueNames
            });
        }
        else alert("Please select two experiment threads with the same value types.");
    },
    //Generates a compiled comparison between experiments selected by the user.
    genList:function(timeNodeList,shallowSearch=false){
        //timeNodeList holds all objects for comparison.
        //Check linearly in each node in all arguments if any names are similiar, we will then go through more
        let nameFrequencies = {};
        let nameList = [];
        for(let i=0;i<timeNodeList.length;i++){
            for(let j=0;j<timeNodeList[i].length;j++){
                if(!nameFrequencies[timeNodeList[i][j].name]){
                    nameFrequencies[timeNodeList[i][j].name] = [i];
                    nameList.push(timeNodeList[i][j].name);
                }
                else nameFrequencies[timeNodeList[i][j].name].push(i);
            }
        }
        //this mode just returns a list of timeNodes that have similar values at the very top of the tree.
        if(shallowSearch){
            let results = [];
            for(let i=0;i<nameList.length;i++){
                if(nameFrequencies[nameList[i]].length > 1){
                    if(results.length == timeNodeList.length)
                        break;
                    timeNodeList.forEach((currNode,index)=>{
                        currNode.forEach(element=>{
                            if(element.name == nameList[i]){
                                //Check to see if this node already exists:
                                let exists = false;
                                for(let j = 0;j<results.length;j++){
                                    if(results[j] == currNode){
                                        exists = true;
                                        break;
                                    }
                                }
                                if(!exists)
                                    results.push(index);
                            }
                        });
                    });
                }
            }
            return results;
        }
        //This is the recursive mode, where a comparison tree is created:
        else{
            let compiledResult = [];
            //See if any of these name appear more than once in these timeNodes, if so, go into a recursive loop in those timeNodes to find more matches:
            nameList.forEach(element=>{
                if(nameFrequencies[element].length > 1){
                    let childElements = [];
                    nameFrequencies[element].forEach(index=>{
                        timeNodeList[index].forEach(timeNodeObject=>{
                            if(timeNodeObject.name == element){
                                childElements.push(timeNodeObject.children);
                            }
                        });
                    });

                    compiledResult.push({name:element,children:this.genList(childElements)});

                }
            });
            return compiledResult;
        }
    },
    //This is different from the regular viewing mode. It creates a custom modelTiming object in order to display multiples at once.
    viewChart:function(id){
        childrenTemp = [];
        expNames = [];
        expNameSort = [];
        this.activeExps = [];
        this.relatedNodes.forEach(element=>{
            if(id=="summaryButton"){
                let resultNode = {children:element[0].timeNodes[element[1]],name:element[0].name+"(Thread "+element[1]+")",values:{}};
                //console.log(resultNode);
                //Fill in pseudo data to meet graph-changing needs: (Averaging with these is not ideal).
                element[0].valueNames.forEach(name=>resultNode.values[name] = 0);
                //if(resultNode.children == 0) childrenTemp.push(resultNode);
                /*else*/ resultNode.children.forEach(this.viewChart_childPrint);
            }
            else if(element[0].nodeTableList[element[1]][id]){
                if(element[0].nodeTableList[element[1]][id].children.length == 0)
                    childrenTemp.push(element[0].nodeTableList[element[1]][id]);
                else element[0].nodeTableList[element[1]][id].children.forEach(this.viewChart_childPrint);
            }
            this.activeExps.push(element);
            this.activeExps["e"+element[0].name] = element;
        });
        expNames.forEach(element=>expNameSort[element].forEach(node=>{
                childrenTemp.push(node);
        }));
        this.exp.currentEntry = {children:childrenTemp,name:(id)};
        this.activeChildren = childrenTemp;
        changeGraph(this.exp.currentEntry);

        //Remove duplicate labels:
        for(let i=0;i<resultChart.data.labels.length;i++){
            if(i!=0){
                nonBlankIndex = i-1;
                while(resultChart.data.labels[nonBlankIndex]=="")
                    nonBlankIndex--;
                if(resultChart.data.labels[i] == resultChart.data.labels[nonBlankIndex]){
                    resultChart.data.labels[i] = "";
                }
            }
        }
        resultChart.update();
    },
    //This is reserved for the viewChart function.
    viewChart_childPrint:node=>{
        let uniqueName = true;
        for(let i=0;i<expNames.length;i++){
            if(expNames[i] == node.name){
                uniqueName = false;
                break;
            }
        }
        if(uniqueName)
                expNames.push(node.name);
        if(!expNameSort[node.name])
            expNameSort[node.name] = [];
            expNameSort[node.name].push(node);
        },
    start:function(){
        if(this.exp.timeNodes[0].length == 0){
            alert("Error: there's nothing to compare.");
            comparisonMode.finish();
        }
        else{
            backButton.style.display="none";
            this.on = true;
            this.exp.view();
            threadSelect.style.display = "none";
            expSelect.style.display = "none";
            setTimeout(()=>{
                if(this.exp.nodeTableList[0][window.location.hash.split("#")[1]] && compare){
                    document.getElementById(window.location.hash.split("#")[1]).click();
                    compare = false;
                }
                else summaryButton.click();

                setTimeout(()=>{
                    //Generate a new link for comparison mode:
                    let newLink = detectRootUrl()+"summary/";
                    let idStr="";
                    let rankStr="";

                    let metaArray = [];
                    this.activeExps.forEach(expArray=>{
                        idStr+=(idStr == ""?"":",")+expArray[0].name;
                        rankStr+=(rankStr == ""?"":",")+expArray[0].rank;
                        metaArray.push(expArray[0]);
                    });
                    metaOpenClose(true,metaArray);
                    mtViewer.closeDlList();
                    history.pushState("","",newLink+idStr+"/"+rankStr+"/compare/"+(compare?window.location.hash:"#summary"));
                },10);
            },10);
            compareButton.innerHTML = "End Comparison";
            compareButton.onclick = ()=>comparisonMode.finish();
        }
    },
    //Close comparison mode and go back to the regular view.
    finish:function(){
        backButton.style.display="";
        threadSelect.style.display = "";
        expSelect.style.display = "";
        compareButton.innerHTML = "Compare";
        compareButton.onclick = ()=>compDivObj.toggle();
        this.on = false;
        switchExperiment(currExp);
    }
}