//Author: Zachary Mitchell
//Purpose: This file holds all of DOM functions in modelTiming.html (It got rather large XP)
var isChrome = /Chrome/.test(navigator.appVersion);
var triggerResize;
var dlLock = true; //Locks dataList in place. If it slides back, so will dataInfo
var dlShow = true;
//These are for data list event listeners:
var dlMouseDown = false;
var dlBarMouseDown = false;
var dlCurrWidth = dataList.style.width;

//This is a quick function to help look for cookies. It's general enough for use anywhere else if needed.
//Regex is required for use, see: https://www.w3schools.com/jsref/jsref_obj_regexp.asp
var cookieSearch = regex=>{
    let result = document.cookie.split(";").find(e=>regex.test(e));
    if(result)
        return result.split("=")[1];
}

//adjust the size of the dataList to reflect the graph's height:
window.onresize = function(){
    if(typeof(paceLoadResize)!=undefined && document.getElementsByClassName("loadScreen").length!=0)
        paceLoadResize();
    dataList.style.height = dataList.style.height;
    dlDisplayButton.style.height = dataList.style.height;
    clearTimeout(triggerResize);
    triggerResize=setTimeout(()=>{
        dataList.style.height = dataInfo.style.height
        dlResizeBar.style.height = dataList.style.height;
        dlResizeBar.style.left = dataInfo.style.left;
        //Datalist and dataInfo wind up using three different units for resizing! ...This changes the measurement again because dataInfo doesn't want to align with datalist otherwise XP
        if(dataInfo.style.width[dataInfo.style.width.length-1] !="%"){
            dataInfo.style.width = (window.innerWidth *.77) / 13 + "em";
            dataInfo.style.left = (window.innerWidth *.22) / 13 + "em";
            backButton.style.left = dataInfo.style.left;
        }
    },10);

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

window.onmousemove = function(){
    if(dlBarMouseDown)
        dataList.style.width = ( (arguments[0].x-32)/13)+'em';
    if(dlLock && dlMouseDown && dataList.style.width !=dlCurrWidth){
        dlCurrWidth = dataList.style.width;
        //This value is for converting back to px:
        let currWidthTemp = (/em/.test(dlCurrWidth)?dlCurrWidth.replace("em","")*13:dlCurrWidth.replace("px","")*1);

        dlResizeBar.style.left = (currWidthTemp+25)+"px";
        dataInfo.style.width = (window.innerWidth - currWidthTemp) + "px";
        dataInfo.style.left = (currWidthTemp + 30) + "px";
        backButton.style.left = (currWidthTemp + 30) + "px";
    }
}

smoothColorsCheck.onclick = function(){
    smoothColors = this.checked;
    document.cookie = "smoothColors="+(smoothColors?1:0)+";path=/summary/";
    colorChart(colorSetting);
    resultChart.update()
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
    if(!listFB)
        dlResizeBar.style.display="none";
    else{
        dlResizeBar.style.display="";
        dlResizeBar.style.left = leftValue;
    }
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
    mtViewer.closeDlList();
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
        let resultElement = document.createElement("div");
        resultElement.className="compareDiv";
        let resultString = "<p style='text-align:right;'><button class='btn btn-default' onclick='this.parentElement.parentElement.outerHTML=\"\";compDivObj.expCountCheck();'>X</button></p><select onchange='compDivObj.updateThreads(this)'>";
            expList.forEach(exp=>{
                resultString+="<option>"+exp.name+"_"+exp.rank+"</option>"
            });
            resultString+="</select><select>";
            expList[0].timeNodes.forEach((element,index)=>resultString+="<option value='"+index+"'>Thread "+index+"</option>");
        resultString+="</select>";
        resultElement.innerHTML=resultString;
        compDivBody.appendChild(resultElement);
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
        document.cookie = "darkMode="+(tf?1:0)+"; path=/summary/";
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
        $(metaInfoTxt.parentElement).slideUp(200);
        setTimeout(()=>metaInfoTxt.innerHTML = outStr,metaInfoTxt.innerHTML == ""?0:200);
        $(metaInfoTxt.parentElement).slideDown(200);
    }
    if(openClose)
        $(metaInfoTxt.parentElement).slideDown(200);
    else
        $(metaInfoTxt.parentElement).slideUp(200);
}

//The interface for the color selection:
var colorSelect = {
    themes:[],
    //Set the colors upon a change. This also get's saved to cookies.
    saveColorConfig:function(updateChart = true,theme = this.themes[colorSThemes.selectedIndex].values){
        hexArray = [];
        for(let i=0;i<theme.length;i++)
            hexArray.push(theme[i]);
        colorConfig = hex2RgbArray(hexArray);
        //In the event that you can't load the chart yet, this is usefull:
        if(updateChart){
            colorChart();
            resultChart.update();
        }
        let cookiePath=";path=/summary/";
        document.cookie = "barTheme="+colorSThemes.selectedIndex+cookiePath;
        document.cookie = "barColors="+hexArray.join()+cookiePath;
    },

    loadThemes:function(){this.themes.forEach(theme=>colorSThemes.innerHTML+="<option"+(theme == this.themes[0]?" selected":"")+">"+theme.name+"</option>")},

    restoreCookies:function(){
        let cookieList = [
            cookieSearch(/barTheme/),
            cookieSearch(/barColors/)
        ];
        if(cookieList[0] && cookieList[1]){
            colorSThemes.selectedIndex = cookieList[0]*1;
            this.saveColorConfig(false,cookieList[1].split(","));
        }
        else colorSelect.saveColorConfig(false);
    },
    getMplTheme:function(name,colorCount = 10){
        $.get("/ajax/getMplColor/"+name+"/"+colorCount,data=>{
            colorArray = JSON.parse(data);
            if(colorArray.length == 0)
                alert("Color not found...");
            else this.saveColorConfig(true,colorArray);
        });
    }
}

$.get("/static/chartJsThemes.json",data=>colorSelect.themes = data);