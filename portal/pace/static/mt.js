//Author: Zachary Mitchell
//Purpose: Create a stucture to Display analytical data based on timeNodes.
var timeNodes = JSON.parse(jsonFile);

//Whichever node is currently selected, it will appear here.
var currentEntry=undefined;
var okToClick=true;
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
/*scope is the range you want the subprocesses to be closed by default. (e.g a range of 0-2 would have the rest of the nodes opened by default by the 3rd layer.)*/
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
            if(currentEntry!=undefined && currentEntry.name == this.id && nodeTable[this.id].children.length > 0){
                let listTag = this.getElementsByTagName("ul")[0].style;
                listTag.display=(listTag.display=="none"?"":"none");
                //Pretty much stops all other clicks from triggering.
                okToClick = false;
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
                setTimeout(()=>{okToClick = true;},10);
                
                //Display appropriate graph info:
                if(nodeTable[this.id].children.length > 0){
                    resultChart.options.title.text=this.id;
                    triggerGraph(nodeTable[this.id]);
                }
            }
        };
        
        //Make more lists:
        if(node.children.length>0){
            listElement.appendChild(htmlList(node.children,scope,currScope+1));
            listElement.getElementsByTagName("span")[0].style.backgroundColor=percentToColor(percentList[percentIndex],true);
            percentIndex++;
            if(currScope >= scope[0] && currScope<=scope[1])
                listElement.getElementsByTagName("ul")[0].style.display="none";
        }
        newList.appendChild(listElement);
    });
    
    return newList;
}

//Display the information in the graph specified by the user:
function triggerGraph(nodeIn,valIn=valueName.children[valueName.selectedIndex].value,dataIndex=0,minMax=false){
    //Get all the children in this node:
    let mtData = [];//Data from mtSum
    let nameLabels=[];
    let updateChart = (minMax?false:true);
    let calledTriggerGraph = false;
    
    //This is where the road changes if min/max is selected. We call another dataset to be generated.
    if(valIn!="min/max" && resultChart.data.datasets.length > 1 && !minMax)
        resultChart.data.datasets.pop();
    else if(valIn == "min/max"){
        resultChart.data.datasets[1]={
            data:[],//Data to be transferred to the chart.
            backgroundColor:[], //These are randomly generated.
            label:"",
            borderWidth:1
        };
        triggerGraph(nodeIn,"max",1,true);
        calledTriggerGraph = true;
        valIn="min";
    }

    nodeIn.children.forEach((child)=>{
        mtData[mtData.length]=mtSum(child,valIn);
        nameLabels[nameLabels.length] = child.name;
    });

    //Take it to chartData based on mode:
    switch(mode.children[mode.selectedIndex].value){
        case "sum":
        let displayIndex = (valIn == "nodes"?1:0);
        for(let i=0;i<mtData.length;i++){
            resultChart.data.datasets[dataIndex].data[i]=mtData[i][displayIndex];
        }
        break;
        case "avg":
        for(let i=0;i<mtData.length;i++){
            resultChart.data.datasets[dataIndex].data[i]=(mtData[i][0] / mtData[i][1]);
        }
        break;
    }

    //Render the chart!
    resultChart.data.labels=nameLabels;
    resultChart.data.datasets[dataIndex].label=mode.children[mode.selectedIndex].value + " - " + valIn;
    resultChart.data.datasets[dataIndex].backgroundColor = [];
    colorSumlist = [];
    mtData.forEach((element)=>{
        colorSumlist.push(element[1]);
    });
    colorPercentages = arrayToPercentages(colorSumlist);
    for(let i=0;i<resultChart.data.datasets[dataIndex].data.length;i++){
        resultChart.data.datasets[dataIndex].backgroundColor.push(percentToColor(colorPercentages[i],true));
    }
    if(updateChart)
        resultChart.update();
}

function rand(num){
    return Math.floor(Math.random()*num);
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
function percentToColor(percentage=50,transparency=false,colors=[[0,0,255],[0,255,0],[255,0,0]]){
    if(percentage > 100)
        percentage=100;
    let resultColor=[];
    //Split 100 up so the given percentage is distributed evenly:
    let subtractValue = 100 / colors.length;
    let difference = percentage;//This will represet a certain percentage of subtractValue.
    let colorIndex=0; //The color we will be transitioning from

    while(difference - subtractValue >= 0){
        difference-=subtractValue;
        if(difference - subtractValue > 0)
        colorIndex++;
    }
    resultColor=colors[colorIndex];
    if(difference!=0){
        for(let i=0;i<resultColor.length;i++){
            resultColor[i]-= Math.floor((colors[colorIndex][i] - colors[colorIndex+1][i]) * (.01* (100 / subtractValue) * difference));
        }
    }
    return "rgba("+resultColor[0]+","+resultColor[1]+","+resultColor[2]+","+(transparency?0.2:1)+")";
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
    valueName.innerHTML+="<option value='"+name+"'>"+name+"</option>";
});
dataList.appendChild(htmlList(timeNodes,[0,2]));