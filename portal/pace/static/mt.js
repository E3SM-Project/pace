//Author: Zachary Mitchell
//Purpose: These are the core functions for displaying everything in modelTiming.html
var timeNodes = JSON.parse(jsonFile);

//Whichever node is currently selected, it will appear here.
var currentEntry=undefined;
var okToClick=true;
var stackedCharts = true;
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
            window.scrollBy(0,-window.innerHeight)
            if(currentEntry!=undefined && currentEntry.name == this.id && nodeTable[this.id].children.length > 0){
                let listTag = this.getElementsByTagName("ul")[0].style;
                listTag.display=(listTag.display=="none"?"":"none");
                //Pretty much stops all other clicks from triggering.
                okToClick = false;
                //Change the url; this would normaly be recursive, but thanks to okToClick, that can all be prevented!
                window.location.hash=this.id;
                setTimeout(()=>{okToClick = true;},10);
            }
            else if(okToClick){
                if (currentEntry == undefined || currentEntry.name!= this.id){
                    this.style.fontWeight="bold";
                    if(currentEntry !=undefined && currentEntry.name !=undefined)
                        document.getElementById(currentEntry.name).style.fontWeight="";
                    currentEntry = nodeTable[this.id];
                }
                okToClick = false;
                window.location.hash=this.id;
                setTimeout(()=>{okToClick = true;},10);
                
                //Display appropriate graph info:
                if(nodeTable[this.id].children.length > 0){
                    resultChart.options.title.text=this.id;
                    //Strange... there's a small chance that something asynchronous will take too long before chart.js can render the chart... LET'S FIX THAT!
                    setTimeout(()=>{changeGraph(nodeTable[this.id]);},10);
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
        if(valIn=="min/max"){
            for(let i=0;i<nodeIn.children.length;i++){
                resultChart.data.labels.push(nodeIn.children[i].name);
                ["min","max"].forEach((minMax)=>{
                    makeGraphBar({children:[nodeIn.children[i]]},minMax,i,(minMax == "min"?0:1));
                });
            }
            colorChart();
            resultChart.data.datasets[0].label="Min";
            resultChart.data.datasets[1].label="Max";
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

var nodeTable = new addressTable(timeNodes,true);
valueList.forEach((name)=>{
    valueName.innerHTML+="<option "+(name=="wallClock"?"selected":"")+" value='"+name+"'>"+name+"</option>";
});
dataList.appendChild(htmlList(timeNodes,[0,2]));
