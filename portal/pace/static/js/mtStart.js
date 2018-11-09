//Author: Zachary Mitchell
//Purpose: Just starting the webpage requires the following syntax:

//Fire up the summary:
$(document).ready(()=>{
    colorSelect.loadThemes();
    colorSelect.restoreCookies();

    var threadList = undefined;
    var onMtPage = true;
    dataInfo.style.height = (window.innerHeight*.8)+"px";
    //safari for IOS is kindof weird with the background colors for dataList, so here's something to change it:
    dataList.style.backgroundColor="white";
    //This time, google chrome is the special snowflake; rendering width and other alignments differ from every other browser:
    if(isChrome){
        dataInfo.style.left = "22%";
        dataInfo.style.width= "77%";
        backButton.style.left = "22%";
    }
    quickSearchContainer.children[0].style.width="15em";
    quickSearchContainer.getElementsByClassName("pTextMenu")[0].style.width="15em";

    //Change the footer due to weird happenings on mobile:
    document.getElementsByClassName("footer")[0].style.zIndex = "-1";
    dmObj.toggle(dmObj.checkCookies());
    dmCheck.checked = dmObj.checkCookies();
    animate();
    if(expData!=undefined){
        for(let i=0;i<expData.length;i++){
            if(i<expData.length-1)
                getExperiment(expData[i][0],expData[i][1],false);
            else{
                getExperiment(expData[i][0],expData[i][1],()=>{
                expDownloadDefault();
                if(threadList){
                    threadList.forEach((element,index)=>{
                        expList[index].currThread = element*1;
                    });
                }
                if(threadList && !compare && threadList.length == expData.length){
                    threadSelect.selectedIndex = threadList[threadList.length-1]*1;
                    threadSelect.onchange();
                }
                if(compare){
                    let resultList = [];
                    expList.forEach( (element,index)=>{
                        resultList.push([element,( (threadList!=undefined && threadList[index]!=undefined) ?threadList[index]*1:0)]);
                    });
                    comparisonMode.new(resultList);
                    comparisonMode.start();
                }
                dlDisplayButton.style.height = dataList.style.height;
            });
            }
        }
    }
    else getExperiment(-1,"0000");
    window.onresize();
});