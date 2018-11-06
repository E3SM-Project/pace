//Author: Zachary Mitchell
//Purpose: This file holds all of DOM functions in modelTiming.html (It got rather large XP)
var isChrome = /Chrome/.test(navigator.appVersion);
var triggerResize;
var dlLock = true; //Locks dataList in place. If it slides back, so will dataInfo
var dlShow = true;
//These are for data list event listeners:
var dlMouseDown = false;
var dlCurrWidth = dataList.style.width;

//adjust the size of the dataList to reflect the graph's height:
window.onresize = function(){
    if(typeof(paceLoadResize)!=undefined && document.getElementsByClassName("loadScreen").length!=0)
        paceLoadResize();
    dataList.style.height = dataList.style.height;
    dlDisplayButton.style.height = dataList.style.height;
    clearTimeout(triggerResize);
    triggerResize=setTimeout(()=>dataList.style.height = dataInfo.style.height,10)

    //Normally, 1 em = 16px, but 13 seems to work better for this scenario :P (See: https://kyleschaeffer.com/development/css-font-size-em-vs-px-vs-pt-vs/)
    if(dlLock){
        dataList.style.width = (window.innerWidth * .2) / 13 + "em";
        if(window.innerWidth < 700){
            toggleDlLock(false);
            dlSlide(false);
        }
    }
    else if(window.innerWidth > 700){
        toggleDlLock(true);
        dlSlide(true);
    }
}
backButton.onclick = function(){
    if(currExp.currentEntry.parent!=undefined){
        if(currExp.currentEntry.name == currExp.currentEntry.parent.name)
            summaryButton.click();
        else document.getElementById(currExp.currentEntry.parent.name).click();
    }
}

dataList.onmousedown = function(){
    dlMouseDown = true;
}
dataList.onmouseup = function(){
    dlMouseDown = false
}

dataList.onmousemove = function(){
    if(dlLock && dlMouseDown && dataList.style.width !=dlCurrWidth){
        dlCurrWidth = dataList.style.width;
        dataInfo.style.width = (window.innerWidth - dataList.style.width.replace("px","")*1) + "px";
        dataInfo.style.left = ((dataList.style.width.replace("px","")*1) + 30) + "px";
        backButton.style.left = ((dataList.style.width.replace("px","")*1) + 30) + "px";
    }
}

//The following is functionality for dataList to slide in and out:
function dlSlide(listFB = !dlShow,infoFB){
    if(infoFB === undefined)
        infoFB = dlLock && listFB?true:false;
    $(dataList).animate((listFB?{left:"2em",width: (dlLock? (window.innerWidth * .2) / 13 + "em":"18em" ) }:{left:"-22em",width:"18em"}),250);
    dlShow = listFB;

    let leftValue = isChrome?"22%":"27%";
    $(dataInfo).animate((infoFB?{left:leftValue,width:isChrome?"77%":"75%"}:{left:"2%",width:"99%"} ),250);
    $(backButton).animate((infoFB?{left:leftValue}:{left:"2%"} ),250);
}

function toggleDlLock(tf = !dlLock){
    dlLock = tf;
    dlSlide(true,dlLock);
}

summaryButton.onclick=function(){
    if(comparisonMode.on)
        comparisonMode.viewChart("summaryButton");
    else{
        let root={children:currExp.timeNodes[currExp.currThread],name:"summaryButton"};
        currExp.currentEntry=root;
        changeGraph(root);
    }
    resultChart.options.title.text=(comparisonMode.on?comparisonMode.exp.name:currExp.name +": "+currExp.rank+ " (Thread "+currExp.currThread+")");
    okToClick = false;
    setTimeout(()=>okToClick = true,10);
    history.replaceState("","",window.location.href.split("#")[0]+(comparisonMode.on && !/compare/.test(window.location.href)?"/compare/":"")+"#summary");
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
//predictive search + quick search functionality:
quickSearchPredict = new predictiveSearch.element(quickSearchBar,"qsb");
quickSearchBar.onkeydown = evt=>{
    quickSearchPredict.keydownListener(evt);
    if(evt.key == "Enter" && quickSearchPredict.allowEnter) quickSearchObj.search(quickSearchBar.value);
};
quickSearchBar.onkeyup = evt=>{
    quickSearchPredict.keyupListener(evt);
    if(quickSearchBar.value!="")
        $.get(detectRootUrl()+"ajax/similarDistinct/"+quickSearchPredict.inputWords[quickSearchPredict.wordIndex],data=>quickSearchPredict.refreshKeywords(JSON.parse(data)));
}
quickSearchBar.onkeyup = evt=>{
    quickSearchPredict.keyupListener(evt);
	if(quickSearchBar.value!="" && quickSearchPredict.enabled)
	if(!/:/.test(quickSearchPredict.inputWords[quickSearchPredict.wordIndex]))
        $.get(detectRootUrl()+"ajax/similarDistinct/"+quickSearchPredict.inputWords[quickSearchPredict.wordIndex],data=>quickSearchPredict.refreshKeywords(JSON.parse(data)));
	else quickSearchPredict.pTextMenu.style.display="none";
}
quickSearchBar.onblur = ()=>setTimeout(()=>predictiveSearch.menuBlur("qsb"),150);

var chartSettings = {
    type: 'horizontalBar',
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
        maintainAspectRatio:false,
        title:{
            display: true,
            text:""
        },
        legend:{
            display:false,
        },
        tooltips:{
            enabled:false
        },
        onClick:(event)=>{
            let activeElement = resultChart.getElementAtEvent(event);
            if(!comparisonMode.on){
                if(activeElement.length > 0){
                    let timeNodeObject = (!stackedCharts 
                        || valueName.children[valueName.selectedIndex].value == "min/max" || 
                        (resultChart.data.datasets.length == 1 && currExp.nodeTableList[currExp.currThread][activeElement[0]._model.label].children.length == 0)?
                        currExp.nodeTableList[currExp.currThread][activeElement[0]._model.label]:
                        currExp.nodeTableList[currExp.currThread][activeElement[0]._model.label].children[activeElement[0]._datasetIndex]);
                    let timeNode = document.getElementById(timeNodeObject.name).getElementsByTagName('ul')[0];
                    parentPath(timeNodeObject).forEach((listName)=>{
                        let listElement = document.getElementById(listName).getElementsByTagName('ul');
                        if(listElement.length > 0)
                            listElement[0].style.display="";
                    });
                    if(okToClick && timeNode!=undefined)
                        timeNode.click();
                }
            }
            else if (activeElement.length>0){
                let evtData = comparisonEvt(activeElement);
                let changeExp = confirm("Clicking Ok will take you to "+evtData.spefExp.name+" (Thread "+evtData.targetNode.thread+") process \""+evtData.targetNode.name+".");
                if(changeExp){
                    //console.log(evtData.nodeObject.name);
                    evtData.spefExp.currThread = evtData.targetNode.thread;
                    evtData.spefExp.currentEntry = evtData.targetNode;
                    currExp = evtData.spefExp;
                    setTimeout(()=>comparisonMode.finish(),10);
                    for(let i=0;i<expSelect.children.length;i++){
                        if(expSelect.children[i].innerHTML == evtData.spefExp.name)
                            expSelect.selectedIndex = i;
                    }
                }
            }
        },
        scales: {
            yAxes: [{stacked:true}],
            xAxes:[
                {stacked:true,position:"top"},
            ]
        }
    }
}

var resultChart = new Chart(chartTag, chartSettings);

//You can't directly define specific variables for some reason when one is highlighted by chart.js, so here's a quick fix:
chartTag.onmousemove = function(event){
    //this should make things clearner to read:
    let valueElement = valueName.children[valueName.selectedIndex];

    let results = resultChart.getElementAtEvent(event);
    if(results.length > 0){
        nodeId.style.left = (event.x + 20)+"px";
        nodeId.style.top = (event.y - 20)+"px";
        let formattedNames = [
            [["Min","min"],["Max","max"]],
            [["WallMin","wallmin"],["WallMax","wallmax"]],
        ];
        let formatNameIndex = 0;
        if(valueElement.value == "wallmin/wallmax")
            formatNameIndex++;

        if(!comparisonMode.on){
            let resultNode = (!stackedCharts ||
                valueElement.value == "min/max" || 
                valueElement.value == "wallmin/wallmax" || 
                resultChart.data.datasets.length == 1?currExp.nodeTableList[currExp.currThread][results[0]._model.label].name:
                currExp.nodeTableList[currExp.currThread][results[0]._model.label].children[results[0]._datasetIndex].name);
            let outputStr = "";
            if(valueElement.value == "min/max" || valueElement.value == "wallmin/wallmax"){
                outputStr=formattedNames[formatNameIndex][0][0]+": "+currExp.nodeTableList[currExp.currThread][resultNode].values[formattedNames[formatNameIndex][0][1]] +
                "<br>"+ formattedNames[formatNameIndex][1][0]+": "+currExp.nodeTableList[currExp.currThread][resultNode].values[formattedNames[formatNameIndex][1][1]];
            }
            else outputStr = valueElement.innerHTML+": "+(valueElement.value == "nodes"?mtSum(currExp.nodeTableList[currExp.currThread][resultNode])[1]: currExp.nodeTableList[currExp.currThread][resultNode].values[valueElement.innerHTML]);
            nodeId.innerHTML=currExp.name+"_"+currExp.rank+"(Thread "+currExp.currThread+")<br>"+resultNode+"<br>"+outputStr;
        }
        else{
            if(results.length > 0){
                let output = comparisonEvt(results);
                //console.log(output);
                let valueStr = "";
                if(valueElement.value == "min/max" || valueElement.value == "wallmin/wallmax"){
                    valueStr=formattedNames[formatNameIndex][0][0]+": "+output.targetNode.values[formattedNames[formatNameIndex][0][1]] +
                "<br>"+ formattedNames[formatNameIndex][1][0]+": "+output.targetNode.values[formattedNames[formatNameIndex][1][1]];
                }
                else valueStr = valueElement.innerHTML+": "+(valueElement.value == "nodes"?mtSum(output.targetNode)[1]:output.targetNode.values[valueElement.innerHTML]);
                nodeId.innerHTML=output.spefExp.name+"_"+output.spefExp.rank+"(Thread "+output.targetNode.thread+")<br>"+output.targetNode.name+"<br>"+valueStr;
            }
        }
    }
    else if(nodeId.innerHTML!="")
        nodeId.innerHTML="";
}

threadSelect.onchange = function(){
    currExp.currThread = threadSelect.children[threadSelect.selectedIndex].value;
    listContent.innerHTML = "";
    listContent.appendChild(currExp.nodeDomList[currExp.currThread]);
    summaryButton.click();
}

//CompareSelectDiv's functions are in here due to potentional naming conflicts.
var compDivObj = {
    display:false,
    toggle:function(){
        //Generate a list of experiments:
        if(compDivBody.innerHTML == "")
            compDivObj.makeExp();
            this.display = !this.display;
            if(this.display)
                compareSelectDiv.style.display = "initial";
            $("#compareSelectDiv").animate({opacity:(compareSelectDiv.style.opacity != "1"?"1":"0")},300,()=>{if(!compDivObj.display) compareSelectDiv.style.display = "none";});
    },
    makeExp:function(){
        let resultString = "<div class='compareDiv'><p style='text-align:right;'><button onclick='this.parentElement.parentElement.outerHTML=\"\";compDivObj.expCountCheck();'>X</button></p><select onchange='compDivObj.updateThreads(this)'>";
            expList.forEach(exp=>{
                resultString+="<option>"+exp.name+"_"+exp.rank+"</option>"
            });
            resultString+="</select><select>";
            expList[0].timeNodes.forEach((element,index)=>resultString+="<option value='"+index+"'>Thread "+index+"</option>");
        resultString+="</select></div>";
        compDivBody.innerHTML+=resultString;
        this.expCountCheck();
    },
    //This name is weird XP
    expCountCheck:function(){
        compareGo.style.display = compDivBody.getElementsByClassName("compareDiv").length < 2?"none":"";
    },
    updateThreads:function(context){
        let resultString = "<select>";
        let ctxThread = context.parentElement.getElementsByTagName("select")[1];
        ctxThread.innerHTML="";
        expList[context.selectedIndex].timeNodes.forEach((element,index)=>resultString+="<option value='"+index+"'>Thread "+index+"</option>");
        ctxThread.innerHTML = resultString+"</select>";
    },
    scan:function(){
        //Create a list of elements to compare based on the input from the selection window:
        resultList = [];
        elements = compDivBody.getElementsByClassName("compareDiv");
        for(let i=0;i<elements.length;i++){
            selectTags = elements[i].getElementsByTagName("select");
            resultList.push([expList[selectTags[0].selectedIndex],selectTags[1].selectedIndex]);
        }
        comparisonMode.new(resultList);
        comparisonMode.start();
        compDivObj.toggle();
    }
}

function updateExpSelect(){
    let resultString = "";
    expList.forEach(element=>resultString +="<option>"+element.name+"_"+element.rank+"</option>"); 
    expSelect.innerHTML = resultString;
}
//This function is for comparison mode; whenever the user clicks or hovers over something, general information is returned to match the functionality of regular viewing.
function comparisonEvt(evt){
    let result = {};
    result.spefExp = comparisonMode.activeChildren[evt[0]._index].srcExp;
    //console.log(comparisonMode.activeChildren[evt[0]._index]);
    result.spefChildIndex = (comparisonMode.activeChildren[evt[0]._index].children.length > 0?evt[0]._datasetIndex:undefined);
    result.targetNode = (result.spefChildIndex!=undefined && stackedCharts?comparisonMode.activeChildren[evt[0]._index].children[result.spefChildIndex]:comparisonMode.activeChildren[evt[0]._index]);
    return result;
}

//This object is for Dark Mode!
var dmObj={
    on:false,
    percentage:0,
    interval:undefined,
    bgcolor:[[255,255,255],[25,25,25]],
    textColor:[[0,0,0],[100,100,100]],
    //Turn dark mode on and off (complete with a smooth transition)
    toggle:function(tf){
        this.on = tf;
        //Change cookies:
        document.cookie = "darkMode="+(tf?1:0)+"; path="+detectRootUrl().replace("https://pace.ornl.gov","")+"summary/";
        clearInterval(dmObj.interval);
        lsBackground.style.backgroundColor = (tf?"rgb(25,25,25)":"white");
        dmObj.interval = setInterval(()=>{
            let percentCondition = (tf?dmObj.percentage!=100:dmObj.percentage!=0);
            if(percentCondition){
                if(tf)
                    dmObj.percentage+=4;
                else dmObj.percentage-=4;
                //Body Colors:
                this.colorElements([[document.body,compareSelectDiv,document.getElementsByClassName("searchMenu")[0],quickSearchBar,dataList]],"backgroundColor",this.bgcolor);
                //textColor
                this.colorElements([[listContent,quickSearchBar],
                document.getElementsByTagName("h2"),
                document.getElementsByClassName("checkboxRow"),
                document.getElementsByClassName("searchItem")],"color",this.textColor);
                //DataList button
                this.colorElements([[dlDisplayButton]],"backgroundColor",[[230,230,230],[50,50,50]]);
            }
            else clearInterval(dmObj.interval);
        },17)
    },
    //This helps clean up the above code in case we have many more things needing to be applied to dark mode:
    colorNegator:function(colorArrayIn,darkOn = this.on, percentIn = this.percentage){
        resultArray = (darkOn? colorArrayIn:[colorArrayIn[0],colorArrayIn[1]]);
        return percentToColor(percentIn,0,0,resultArray);
    },
    //Arrays/htmlCollections go in, and everything's colored accordingly:
    colorElements:function(elements,varStr,colorArray){
        //Elements is an array of arrays: each array contains a list of elements requested for coloring:
        //varStr is what you want to color: (e.g "backgroundColor", "color")
        elements.forEach(elementArray=>{
            if(elementArray!=undefined){
                for(let i=0;i<elementArray.length;i++){
                    if(elementArray[i]!=undefined)
                        elementArray[i].style[varStr] = dmObj.colorNegator(colorArray);
                }
            }
        });

    },
    //Check to see what mode the user was on last time the page loaded.
    checkCookies:function(){
        let cookies = document.cookie.split(";");
        let cookieRegex = /darkMode/;
        let result = false;
        cookies.forEach(element=>{
            if(cookieRegex.test(element)){
                if(element.split("=")[1]=='1') result=true;
            }
        });
        return result;
    }
};
var resizeChartVal = 1;
//The sole purpose of this function is to help with the really weird quirk that happens when the chart resizes within a scalable div :/
function resizeChart(dataSetCount = resultChart.data.datasets[0].data.length){
    resizeChartVal = dataSetCount;
    let multiplier = (dataSetCount < 25?.75:dataSetCount/25);
    chartTag.style.height = (window.innerHeight * multiplier)+"px";
    dataInfo.style.height = (parseFloat(dataInfo.style.height.replace("px","")) - 1)+"px";
    setTimeout(()=>dataInfo.style.height = (parseFloat(dataInfo.style.height.replace("px","")) +1)+"px",10);
}

//Zoom in and out of the chart through a nifty shortcut.
dataInfo.onwheel = function(evt){
    if(evt.altKey){
        evt.preventDefault();
        resizeChartVal= (evt.deltaY < 0?resizeChartVal+25:resizeChartVal-25);
        if(resizeChartVal < 0)
            resizeChartVal = 1;
        resizeChart(resizeChartVal);
    }
}

//Open and close the meta-info box
function metaOpenClose(openClose=false,compset,res,expid){
    if(compset && res && expid){
        let outStr = "Compset: <a href='"+detectRootUrl()+"advsearch/compset:"+compset+"'>"+compset+"</a> Res: <a href='"+detectRootUrl()+"advsearch/res:"+res+"'>"+res+"</a> (<a href='"+detectRootUrl()+"exp-details/"+expid+"'>Details</a>)";
        $(metaInfoTxt.parentElement).slideUp(200);
        setTimeout(()=>metaInfoTxt.innerHTML = outStr,metaInfoTxt.innerHTML == ""?0:200);
        $(metaInfoTxt.parentElement).slideDown(200);
    }
    if(openClose)
        $(metaInfoTxt.parentElement).slideDown(200);
    else
        $(metaInfoTxt.parentElement).slideUp(200);
}