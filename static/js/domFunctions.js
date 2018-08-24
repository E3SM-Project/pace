//Author: Zachary Mitchell
//Purpose: This file holds all of DOM functions in modelTiming.html (It got rather large XP)
var triggerResize;
//adjust the size of the dataList to reflect the graph's height:
window.onresize = function(){
        if(typeof(paceLoadResize)!=undefined && document.getElementsByClassName("loadScreen").length!=0)
            paceLoadResize();
        dataList.style.height = chartTag.style.height;
        clearTimeout(triggerResize);
        triggerResize=setTimeout(()=>{dataList.style.height = chartTag.style.height;},10)
}
backButton.onclick = function(){
    if(currExp.currentEntry.parent!=undefined){
        if(currExp.currentEntry.name == currExp.currentEntry.parent.name)
            summaryButton.click();
        else document.getElementById(currExp.currentEntry.parent.name).click();
    }
}

summaryButton.onclick=function(){
    if(comparisonMode.on)
        comparisonMode.viewChart("summary");
    else{
        let root={children:currExp.timeNodes[currExp.currThread],name:"summaryButton"};
        changeGraph(root);
        currExp.currentEntry=root;
    }
    resultChart.options.title.text=(comparisonMode.on?comparisonMode.exp.name:currExp.name + " (Thread "+currExp.currThread+")");
    okToClick = false;
    setTimeout(()=>{okToClick = true;},10);
    window.location.hash="summary";
}

window.onhashchange = function(event = undefined){
    if(event)
        event.preventDefault();
    window.scrollBy(0,-window.innerHeight)
    let clickID = "";
    let hash = window.location.hash.split("#");
    switch(hash[hash.length-1]){
        case "root":
        case "summary":
        clickID="summaryButton"
        break;
        default:
        clickID = hash[hash.length-1];
    }
    if(document.getElementById(clickID)!=undefined && okToClick)
        document.getElementById(clickID).click();
};
var resultChart = new Chart(chartTag, {
        type: 'bar',
        data: {
            labels: [],
            datasets: [{
                label:"",
                data: [],
                backgroundColor: [],
                borderColor: [],
                borderWidth: 1
            }]
        },
        options: {
            title:{
                display: true,
                text:""
            },
            legend:{
                display:false,
            },
            onClick:(event)=>{
                let activeElement = resultChart.getElementAtEvent(event);
                if(activeElement.length > 0){
                    let timeNodeObject = (!stackedCharts || valueName.children[valueName.selectedIndex].value == "min/max" || (resultChart.data.datasets.length == 1 && currExp.nodeTableList[currExp.currThread][activeElement[0]._model.label].children.length == 0)?currExp.nodeTableList[currExp.currThread][activeElement[0]._model.label]:currExp.nodeTableList[currExp.currThread][activeElement[0]._model.label].children[activeElement[0]._datasetIndex]);
                    let timeNode = document.getElementById(timeNodeObject.name).getElementsByTagName('ul')[0];
                    parentPath(timeNodeObject).forEach((listName)=>{
                        let listElement = document.getElementById(listName).getElementsByTagName('ul');
                        if(listElement.length > 0)
                            listElement[0].style.display="";
                    });
                    if(okToClick && timeNode!=undefined)
                        timeNode.click();
                }
            },
            scales: {
                yAxes: [{stacked:true}],
                xAxes:[{stacked:true}]
            }
        }
    });
//You can't directly define specific variables for some reason when one is highlighted by chart.js, so here's a quick fix:
chartTag.onmousemove = function(event){
    let results = resultChart.getElementAtEvent(event);
    if(results.length > 0)
        nodeId.innerHTML=(!stackedCharts || valueName.children[valueName.selectedIndex].value == "min/max" || resultChart.data.datasets.length == 1?currExp.nodeTableList[currExp.currThread][results[0]._model.label].name:currExp.nodeTableList[currExp.currThread][results[0]._model.label].children[results[0]._datasetIndex].name);
    else if(nodeId.innerHTML!="")
        nodeId.innerHTML="";
}

threadSelect.onclick = function(){
    currExp.currThread = threadSelect.children[threadSelect.selectedIndex].value;
    listContent.innerHTML = "";
    listContent.appendChild(currExp.nodeDomList[currExp.currThread]);
    summaryButton.click();
}
function compDivToggle(){
    //Generate a list of experiments:
    if(compDivBody.innerHTML == "")
        makeExpSelect();
    $("#compareSelectDiv").animate({opacity:(compareSelectDiv.style.opacity == "0"?"1":"0")},300);
}

function makeExpSelect(){
    let resultString = "<div class='compareDiv'><p style='text-align:right;'><button onclick='this.parentElement.parentElement.outerHTML=\"\";'>X</button></p><select onchange='updateThreadCount(this)'>";
        expList.forEach(exp=>{
            resultString+="<option>"+exp.name+"</option>"
        });
        resultString+="</select><select>";
        expList[0].timeNodes.forEach((element,index)=>{
            resultString+="<option value='"+index+"'>Thread "+index+"</option>";
        });
    resultString+="</select></div>";
    compDivBody.innerHTML+=resultString;
}
function updateThreadCount(context){
    let resultString = "<select>";
    let ctxThread = context.parentElement.getElementsByTagName("select")[1];
    ctxThread.innerHTML="";
    expList[context.selectedIndex].timeNodes.forEach((element,index)=>{
        resultString+="<option value='"+index+"'>Thread "+index+"</option>";
    });
    ctxThread.innerHTML = resultString+"</select>";
}

function scanCompDiv(){
    //Create a list of elements to compare based on the input from the selection window:
    resultList = [];
    elements = compDivBody.getElementsByClassName("compareDiv");
    for(let i=0;i<elements.length;i++){
        selectTags = elements[i].getElementsByTagName("select");
        resultList.push([expList[selectTags[0].selectedIndex],selectTags[1].selectedIndex]);
    }
    comparisonMode.new(resultList);
    comparisonMode.start();
    compDivToggle();
}

window.onresize();