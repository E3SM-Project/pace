//Author: Zachary Mitchell
//Purpose: This file holds all of DOM functions in modelTiming.html (It got rather large XP)
backButton.onclick = function(){
    if(currentEntry.parent!=undefined){
        if(currentEntry.name == currentEntry.parent.name)
            summaryButton.click();
        else document.getElementById(currentEntry.parent.name).click();
    }   
}

summaryButton.onclick=function(event){
    event.preventDefault();
    let root={children:timeNodes[currThread]};
    resultChart.options.title.text='Model Timing';
    changeGraph(root);currentEntry=root;
    okToClick = false;
    setTimeout(()=>{okToClick = true;},10);
    window.location.hash="summary";
}

window.onhashchange = function(){
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
                    let timeNodeObject = (!stackedCharts || valueName.children[valueName.selectedIndex].value == "min/max" || (resultChart.data.datasets.length == 1 && nodeTableList[currThread][activeElement[0]._model.label].children.length == 0)?nodeTableList[currThread][activeElement[0]._model.label]:nodeTableList[currThread][activeElement[0]._model.label].children[activeElement[0]._datasetIndex]);
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
                yAxes: [{stacked:true,}],
                xAxes:[{stacked:true}]
            }
        }
    });
//You can't directly define specific variables for some reason when one is highlighted by chart.js, so here's a quick fix:
chartTag.onmousemove = function(event){
    let results = resultChart.getElementAtEvent(event);
    if(results.length > 0)
        nodeId.innerHTML=(!stackedCharts || valueName.children[valueName.selectedIndex].value == "min/max" || resultChart.data.datasets.length == 1?nodeTableList[currThread][results[0]._model.label].name:nodeTableList[currThread][results[0]._model.label].children[results[0]._datasetIndex].name);
    else if(nodeId.innerHTML!="")
        nodeId.innerHTML="";
}

threadSelect.onclick = function(){
    currThread = threadSelect.children[threadSelect.selectedIndex].value;
    listContent.innerHTML = "";
    listContent.appendChild(nodeDomList[currThread]);
    summaryButton.click();
}