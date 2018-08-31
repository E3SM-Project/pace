//Author: Zachary Mitchell
//Purpose: These are the core functions for displaying everything in modelTiming.html

var okToClick=true;
var stackedCharts = true;
var currExp;
var expList = [];

//A backlog of things to do when all experiments are retrieved. It is cleared out afterwards.
var expGetCount = 0;
var expGetFunc = [];

//This will be where we look for a specific node. (Making the structured time-node into something linear at the same time)
function addressTable(vals=undefined,jsonArray=false){
    this.length = function (){
        let count = 0
        while (this[count] !=undefined){
            count++;
        }
        return count
    }
    //It appears that all names for nodes are unique! Let's make use of that...
    this.addVals = function(jsonIn,jsonArray = false,parent=undefined){
        if(jsonArray){
            jsonIn.forEach((element)=>{this.addVals(element);});
        }
        else{
            //The awesomness of Javascript allows us to iterate AND call objects by name
            this[jsonIn.name] = jsonIn;
            this[this.length()] = jsonIn;
            jsonIn.children.forEach((child)=>{
                this.addVals(child,false,jsonIn);
            });
            //Making Parents...
            this[jsonIn.name].parent=(parent==undefined?jsonIn:parent);
        }
    }
    if(vals)
        this.addVals(vals,jsonArray)
}

//This holds a single experiment. The goal is to be able to compare multiples, so they are compartmentelized here.
function experiment(timeNodes,valueNames,name = "Unnamed Experiment",rank = "0000"){
    this.name = name;
    this.rank = rank;
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
    this.valueNames = valueNames;

    //Construct:
    this.timeNodes.forEach((thread,i)=>{
        this.nodeTableList.push(new addressTable(thread,true));
        this.nodeDomList.push(htmlList(thread,[0,2]));
        this.threadSelectInner+="<option "+ (!i?"selected":"")+" value="+i+" >Thread "+i+"</option>";
    });
    this.valueNames.forEach((name)=>{
        this.valueSelectInner+="<option "+(name=="wallClock" || name=="wallmax"?"selected":"")+" value='"+name+"'>"+name+"</option>";
    });
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
    $.get(detectRootUrl()+"mtQuery/"+expSrc+"/"+extSrc+"/",function(data,status){
        if(status == "success"){
            //console.log(data);
            results = JSON.parse(data);
            expList.push(new experiment(results[0],results[1],results[2],results[3]));
        }
        expGetCount--;
        if(expGetCount == 0){
            expGetFunc.forEach((element)=>{
                element();
            });
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
    if(window.location.hash==""  || expList.length > 1)
        summaryButton.click();
    else window.onhashchange();
    expSelect.selectedIndex = expList.length-1;
    }

function switchExperiment(index = expSelect.selectedIndex){
    currExp = (typeof(index) == "object"?index:expList[index]);
    currExp.view();
    if(currExp.currentEntry == undefined)
        summaryButton.click();
    else changeGraph( (currExp.currentEntry.children.length == 0?{children:currExp.currentEntry}:currExp.currentEntry) );
    resultChart.options.title.text=currExp.name +": "+currExp.rank+ " (Thread "+currExp.currThread+")";
}

//This creates an HTML list that directly associates with the address table (which in-turn addresses to the original json file). When a tag is clicked, the other lists witihin it are collapsed.
//scope is the range you want the subprocesses to be closed by default. (e.g a range of 0-2 would have the rest of the nodes opened by default by the 3rd layer.)
function htmlList(jsonList,scope=[0,0],currScope=0){
    let newList = document.createElement("ul");

    //Add colors to each element on the list as long as it contains children:
    let sumList = [];
    jsonList.forEach((child)=>{
        sumList.push(mtSum(child)[1]);
    });
    let percentList=arrayToPercentages(sumList);
    let percentIndex=0;
    //List of nodes go inside...
    jsonList.forEach((node)=>{
        let listElement = document.createElement("li");
        listElement.id=node.name;
        listElement.innerHTML+="<span>"+node.name+"</span>";
        listElement.onclick = function(){
            targetExp = (comparisonMode.on?comparisonMode.exp:currExp);
            if(targetExp.currentEntry!=undefined && targetExp.currentEntry.name == this.id && targetExp.nodeTableList[targetExp.currThread][this.id].children.length > 0){
                let listTag = this.getElementsByTagName("ul")[0].style;
                listTag.display=(listTag.display=="none"?"":"none");
                //Pretty much stops all other clicks from triggering.
                okToClick = false;
                //Change the url; this would normaly be recursive, but thanks to okToClick, that can all be prevented!
                window.location.hash=this.id;
                setTimeout(()=>{okToClick = true;},10);
            }
            else if(okToClick){
                if (targetExp.currentEntry == undefined || targetExp.currentEntry.name!= this.id){
                    this.style.fontWeight="bold";
                    if(targetExp.currentEntry !=undefined && targetExp.currentEntry.name !=undefined)
                        document.getElementById(targetExp.currentEntry.name).style.fontWeight="";
                    targetExp.currentEntry = targetExp.nodeTableList[targetExp.currThread][this.id];
                }
                okToClick = false;
                window.location.hash=this.id;
                setTimeout(()=>{okToClick = true;},10);
                
                //Display appropriate graph info:
                if(targetExp.nodeTableList[targetExp.currThread][this.id].children.length > 0){
                    resultChart.options.title.text=this.id;
                    if(comparisonMode.on)
                        setTimeout(()=>{comparisonMode.viewChart(this.id);},10);
                    //Strange... there's a small chance that something asynchronous will take too long before chart.js can render the chart... LET'S FIX THAT!
                    else setTimeout(()=>{changeGraph(currExp.nodeTableList[currExp.currThread][this.id]);},10);
                }
                else{
                    if(comparisonMode.on)
                        setTimeout(()=>{comparisonMode.viewChart(this.id);},10);
                    else setTimeout(()=>{changeGraph({children:[currExp.nodeTableList[currExp.currThread][this.id]]});},10);
                }
            }
        };
        
        //Make more lists:
        if(node.children.length>0){
            listElement.appendChild(htmlList(node.children,scope,currScope+1));
            listElement.getElementsByTagName("span")[0].style.backgroundColor=percentToColor(percentList[percentIndex],.2);
            if(currScope >= scope[0] && currScope<=scope[1])
                listElement.getElementsByTagName("ul")[0].style.display="none";
        }
        newList.appendChild(listElement);
        percentIndex++;
    });
    
    return newList;
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
                minmaxArray[minmaxIndex].forEach((minMax,index)=>{
                    makeGraphBar({children:[nodeIn.children[i]]},minMax,i,index);
                });
            }
            colorChart();
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
            colorChart(stackedBar);
        }
    resultChart.update();
}

//Creates a row of information based on the selected index.
function makeGraphBar(nodeIn,valIn="nodes",dataIndex=0,stackOffset=0){
    // console.log(nodeIn.children);
    //Get all the children in this node:
    let mtData = [];//Data from mtSum
    nodeIn.children.forEach((child)=>{
        mtData.push(mtSum(child,valIn));
    });

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
function colorChart(vertical=true){
    //console.log(resultChart.data.datasets);
    if(vertical){
        for(let i=0;i<resultChart.data.datasets[0].data.length;i++){
        let colorSumlist = [];
        for(let j=0;j<resultChart.data.datasets.length;j++){
            colorSumlist.push(resultChart.data.datasets[j].data[i]);
        }
        let colorPercentages = arrayToPercentages(colorSumlist);
        for(let j=0;j<resultChart.data.datasets.length;j++){
                let colorData = percentToColor(colorPercentages[j],.2,2);
                resultChart.data.datasets[j].backgroundColor.push(colorData[0]);
                resultChart.data.datasets[j].borderColor.push(percentToColor(50,.2,0,[colorData[1],[0,0,0]]));
            }
        }
    }
    else{
        //Same thing, except we're only looking at one layer
            let colorSumlist = [];
            for(let j=0;j<resultChart.data.datasets[0].data.length;j++){
                colorSumlist.push(resultChart.data.datasets[0].data[j]);
            }
            let colorPercentages = arrayToPercentages(colorSumlist);
            for(let j=0;j<resultChart.data.datasets[0].data.length;j++){
                    let colorData = percentToColor(colorPercentages[j],.2,2);
                    resultChart.data.datasets[0].backgroundColor.push(colorData[0]);
                    resultChart.data.datasets[0].borderColor.push(percentToColor(50,.2,0,[colorData[1],[0,0,0]]));
                }
    }
}

//Grabs the values needed from the timeNode tree(This is a direct port from what was used in modelTiming.py)
function mtSum(nodeIn,valName="nodes"){
    let total=0;
    let nodeCount=1;
    nodeIn.children.forEach((child)=>{
        let output = mtSum(child,valName);
        total+=output[0];
        nodeCount+=output[1];
    });
    if (valName!="nodes")  
        total+=nodeIn.values[valName];
    return [total,nodeCount];
}

//Go backwards in a node to get a path from the parent to the child.
function parentPath(nodeIn,currValues=[]){
        currValues.push(nodeIn.name)
        if(nodeIn.name == nodeIn.parent.name)
            return currValues
        currValues = parentPath(nodeIn.parent,currValues);
        return currValues
}

//return an rgb-based color string based on a percentage provided by the user:
function percentToColor(percentage=50,transparency=false,returnType=0,colors=[[0,0,255],[0,255,0],[255,0,0]]){
    if(percentage > 100)
        percentage=100;
    let subtractValue = 100 / (colors.length-1);
    let difference = 0;//This will represet a certain percentage of subtractValue.
    let colorIndex=0; //The color we will be transitioning from.

    //Add up the subtract values until we have one that's greater than (or matches) the percentage:
        for(let i=0;i<colors.length;i++){
            if(percentage >= subtractValue * i){
                colorIndex = i;
                difference = (subtractValue * (i+1) ) - percentage;
            }
            else break;
        }
    let resultColor=colors[colorIndex].slice();
    let colorPercent = .01 * ( (100 / subtractValue) * (subtractValue-difference));
    if(percentage!=100){
        for(let i=0;i<resultColor.length;i++){
            resultColor[i]-=Math.floor( (resultColor[i] - colors[colorIndex+1][i]) * colorPercent );
        }
    }
    //This value is optional; if returnType is > 0, you optionally get the raw values as well.
    let resultColorString;
    if(returnType!=1)
        resultColorString = "rgba("+resultColor[0]+","+resultColor[1]+","+resultColor[2]+","+(transparency?transparency:1)+")";
    return (returnType == 0?resultColorString:returnType==1?resultColor:[resultColorString,resultColor]);
}

//Grabs the ratio of all values inserted, and compares them.
function arrayToPercentages(arrayIn){
    //Compare the node count, find the largest, and make percentages based off of those numbers
    let ratioVals=[];
    let biggestNumber = 0;
    arrayIn.forEach((element)=>{
        if(element > biggestNumber)
            biggestNumber = element;
    });

    arrayIn.forEach((element)=>{
        ratioVals.push((100/biggestNumber)*element);
    })
    return ratioVals;
}

var comparisonMode = {
    on:false,
    exp:undefined,
    relatedNodes:[],
    activeExps:undefined,
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
            expList.forEach(exp=>{
                timeNodeList.push(exp[0].timeNodes[exp[1]]);
            });
            let relNodeTemp = this.genList(timeNodeList,true);
            this.relatedNodes = [];
            relNodeTemp.forEach(element=>{
                this.relatedNodes.push(expList[element]);
            });
            let compareName = "Comparison: ";
            let firstStr = true;
            this.relatedNodes.forEach(exp=>{
                compareName+=(firstStr?"":",")+exp[0].name+"_"+exp[0].rank+"(thread "+exp[1]+")";
                firstStr = false;
            })
            this.exp = new experiment([this.genList(timeNodeList)],expList[0][0].valueNames,compareName,(expList[0][0].rank == "stats"?"stats":"0000"));
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
    viewChart:function(id){
        childrenTemp = [];
        this.activeExps = [];
        this.relatedNodes.forEach(element=>{
            if(id=="summaryButton"){
                let resultNode = {children:element[0].timeNodes[element[1]],name:element[0].name+"(Thread "+element[1]+")",values:{}};
                //Fill in pseudo data to meet graph-changing needs: (Averaging with these is not ideal).
                element[0].valueNames.forEach(name=>{
                    resultNode.values[name] = 0;
                });
                childrenTemp.push(resultNode);
                this.activeExps.push(element);
            }
            else if(element[0].nodeTableList[element[1]][id]){
                childrenTemp.push(element[0].nodeTableList[element[1]][id]);
                this.activeExps.push(element);
            }
        });
        this.exp.currentEntry = {children:childrenTemp,name:(id)};
        changeGraph(this.exp.currentEntry);
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
        summaryButton.click();
        compareButton.innerHTML = "End Comparison";
        compareButton.onclick = ()=>{comparisonMode.finish()};
        }
    },
    finish:function(){
        backButton.style.display="";
        this.on = false;
        threadSelect.style.display = "";
        expSelect.style.display = "";
        compareButton.innerHTML = "Compare";
        compareButton.onclick = ()=>{compDivObj.toggle()};
        switchExperiment(currExp);
    }
}