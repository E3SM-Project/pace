//Author: Zachary Mitchell
//Purpose: create a querying interface for the search bar! This should pull up any relavent experiments; if one is selected, you can choose to view/compare it.
var quickSearchObj = {
    searchData:[],
    rankData:[],
    lastRankIndex:[0,0],
    click:false,
    bodyClick:false,
    mouseCoord:[],
    searchCoord:[],
    doComparison:false,
    searchDataSelected:0,
    search:function(searchStr,limit = 10){
        console.log("%cHELLOOO!!","font-size:175%"); //This is VERY important part of the function.
        if(searchStr == ""){
            if(document.getElementsByClassName("searchMenu").length > 0)
                document.getElementsByClassName("searchMenu")[0].style.display = "none";
        }
        else{
            $.get(detectRootUrl()+"ajax/search/"+searchStr.replace(" ","+")+"/"+limit,(data)=>{
            let resultData = JSON.parse(data)
            this.searchData = resultData[0];
            this.rankData = resultData[1];
            let resultBody = document.createElement("div");
            resultBody.className = "searchBody";
            resultBody.onmousedown = this.searchBodymD;
            resultBody.onmouseup = this.searchBodymU;
            this.searchData.forEach( (element,index) => {
                let searchResult = document.createElement("div");
                searchResult.className = "searchItem";
                searchResult.value = index;
                searchResult.innerHTML+="<a href='"+detectRootUrl()+"exp-details/"+element.expid+"' target='_blank' title='Click here for more details.'><h4>"+element.expid+"</h4></a>User: "+element.user+"</h3><br>Machine:"+element.machine;
                checkStr = "<div style='display:inline-block;margin-left:5px'>";
                quickSearchObj.rankData[index][0].forEach( rank=>{
                    checkStr+="<span style='margin-right:5px'><b>"+rank+"</b><input type='checkbox' onchange='quickSearchObj.scanChecks()'/></span>";
                });
                searchResult.innerHTML+=checkStr+"</div>";
                resultBody.appendChild(searchResult);
            });

            //Generate the search page object:
            let resultPage;
            if(document.getElementsByClassName("searchMenu").length == 0){
                resultPage = document.createElement("div");
                resultPage.className = "searchMenu";
                resultPage.innerHTML+="<div id='searchBodyContainer'></div>"
                //Add Listeners:
                resultPage.onmousedown = this.searchMouseDown;
                resultPage.onmouseup = this.searchMouseUp;
                resultPage.onmousemove = this.searchMouseMove;
                //resultPage.onmouseout = this.searchMouseOut;
                resultPage.innerHTML+="<a><button id='searchCompareBtn' disabled>compare</button></a><a><button id='searchViewBtn' disabled>View</button></a>";
                quickSearchContainer.appendChild(resultPage);
            }
            else{
                resultPage = document.getElementsByClassName("searchMenu")[0];
                searchBodyContainer.innerHTML="";
                if(resultPage.style.display == "none"){
                    resultPage.style.display = "";
                searchViewBtn.disabled = true;
                searchCompareBtn.disabled = true;
                }
            }
            searchBodyContainer.appendChild(resultBody);
            if(dmObj.on){
                document.getElementsByClassName("searchMenu")[0].style.backgroundColor="rgb(25,25,25)";
                var searchItems = document.getElementsByClassName("searchItem");
                for(let i=0;i<searchItems.length;i++){
                    searchItems[i].style.color = "rgb(100,100,100)";
                }
            }
        });
        }
    },
    //functions to help it detect if resultPage is being dragged:
    searchMouseDown:function(){
        quickSearchObj.click = true;
    },
    searchMouseUp:function(){
        quickSearchObj.click = false;
        quickSearchObj.mouseCoord = [];
    },
    searchMouseOut:function(evt){
        quickSearchObj.mouseCoord = [];
        quickSearchObj.searchMouseMove(evt);
    },
    searchMouseMove:function(evt){
        if(quickSearchObj.click && !quickSearchObj.bodyClick){
            if(quickSearchObj.mouseCoord.length == 0){
                quickSearchObj.mouseCoord[0] = evt.x;
                quickSearchObj.mouseCoord[1] = evt.y;
            }
            if(quickSearchObj.searchCoord.length == 0){
                quickSearchObj.searchCoord[0] = (quickSearchObj.mouseCoord[0] *.78);
                quickSearchObj.searchCoord[1] = (quickSearchObj.mouseCoord[1] *.47);
            }
            quickSearchObj.searchCoord[0]-= (quickSearchObj.mouseCoord[0] - evt.x);
            quickSearchObj.searchCoord[1]-= (quickSearchObj.mouseCoord[1] - evt.y);
            quickSearchObj.mouseCoord[0] = evt.x;
            quickSearchObj.mouseCoord[1] = evt.y;
            this.style.left = quickSearchObj.searchCoord[0]+"px";
            this.style.top = quickSearchObj.searchCoord[1]+"px";
        }
    },
    searchBodymD:function(){
        quickSearchObj.bodyClick = true;
    },
    searchBodymU:function(){
        quickSearchObj.bodyClick = false;
    },
    scanChecks:function(){
        let searchResults = document.getElementsByClassName("searchItem");
        for(let i=0;i<this.searchData.length;i++){
            let checkboxes = searchResults[i].getElementsByTagName("input");
            this.rankData[i][1] = [];
            for(let j=0;j<this.rankData[i][0].length;j++){
                if(checkboxes[j].checked){
                    this.rankData[i][1][j] = true;
                    //Record the indexes so we can perform an action when we hit this set.
                    this.lastRankIndex[0] = i;
                    this.lastRankIndex[1] = j;
                }
            }
        }
        let foundStats = false;
        let foundRegular = false;
        let rankCount = 0;
        //Check to see if anything can be compared or viewed:
        for(let i=0;i<this.rankData.length;i++){
            for(let j=0;j<this.rankData[i][0].length;j++){
                if(this.rankData[i][1][j]){
                    searchViewBtn.disabled = false;
                    if(this.rankData[i][0][j] == "stats")
                        foundStats = true;
                    else foundRegular = true;
                    rankCount++;
                }
                if(foundRegular && foundStats)
                    break;
            }
        }
        if(foundStats && foundRegular){
            searchCompareBtn.disabled = true;
        }
        else if(foundStats || foundRegular){
            searchCompareBtn.disabled = rankCount > 1?false:true;
            searchViewBtn.disabled = false;
        }
        else{
            searchCompareBtn.disabled = true;
            searchViewBtn.disabled = true;
        }

        searchViewBtn.onclick = ()=>{quickSearchObj.doAction()};
        searchCompareBtn.onclick = ()=>{quickSearchObj.doAction(true)};
    },
    doAction:function(compToggle = false){
        quickSearchObj.doComparison = compToggle;
        //Scan through everything and dump it into a url. If we're on the modelTiming webpage, it will be separate calls to the server instead:
        document.getElementsByClassName("searchMenu")[0].style.display="none";
        animate();
        searchViewBtn.parentElement.href="#";
        searchCompareBtn.parentElement.href="#";
        this.searchDataSelected = 0;
        for(let i=0;i<quickSearchObj.rankData.length;i++){
            for(let j=0;j<quickSearchObj.rankData[i][0].length;j++){
                if(quickSearchObj.rankData[i][1][j]){
                    this.searchDataSelected++;
                    getExperiment(quickSearchObj.searchData[i].expid,quickSearchObj.rankData[i][0][j],(i == quickSearchObj.lastRankIndex[0] && j == quickSearchObj.lastRankIndex[1])?quickSearchObj.postAction:false);
                }
            }
        }
    },
    postAction:function(){
        expDownloadDefault();
        compView = [];
        if(quickSearchObj.doComparison){
            for(let i=expList.length-quickSearchObj.searchDataSelected;i<expList.length;i++){
                compView.push([expList[i],expList[i].currThread]);
            }
            comparisonMode.new(compView);
            comparisonMode.start();
        }
    }
}
