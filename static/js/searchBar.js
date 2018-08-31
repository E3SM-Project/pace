//Author: Zachary Mitchell
//Purpose: create a querying interface for the search bar! This should pull up any relavent experiments; if one is selected, you can choose to view/compare it.
var searchObj = {
    searchData:[],
    rankData:[],
    lastRankIndex:[0,0],
    click:false,
    bodyClick:false,
    mouseCoord:[],
    searchCoord:[],
    doComparison:false,
    search:function(searchStr,limit = 20){
        console.log("HI SARAAAAT!");
        if(searchStr == ""){
            if(document.getElementsByClassName("searchMenu").length > 0)
                document.getElementsByClassName("searchMenu")[0].style.display = "none";
        }
        else{
            $.get("https://pace.ornl.gov/dev2/ajax/search/"+searchStr.replace(" ","+")+"/"+limit,(data)=>{
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
                searchResult.innerHTML+="<a href='/exp-details/"+element.expid+"' target='_blank' title='Click here for more details.'><h4>"+element.expid+"</h4></a>User: "+element.user+"</h3><br>Machine:"+element.machine;
                checkStr = "<div style='display:inline-block;margin-left:5px'>";
                searchObj.rankData[index][0].forEach( rank=>{
                    checkStr+="<span style='margin-right:5px'><b>"+rank+"</b><input type='checkbox' onchange='searchObj.scanChecks()'/></span>";
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
                document.body.appendChild(resultPage);
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
        });
        }
    },
    //Tames the beast known as bootstrap:
    listenerStop:function(evt){
        evt.preventDefault();
        searchObj.search(searchBar.value);
    },
    //functions to help it detect if resultPage is being dragged:
    searchMouseDown:function(){
        searchObj.click = true;
    },
    searchMouseUp:function(){
        searchObj.click = false;
        searchObj.mouseCoord = [];
    },
    searchMouseOut:function(evt){
        searchObj.mouseCoord = [];
        searchObj.searchMouseMove(evt);
    },
    searchMouseMove:function(evt){
        if(searchObj.click && !searchObj.bodyClick){
            if(searchObj.mouseCoord.length == 0){
                searchObj.mouseCoord[0] = evt.x;
                searchObj.mouseCoord[1] = evt.y;
            }
            if(searchObj.searchCoord.length == 0){
                searchObj.searchCoord[0] = (searchObj.mouseCoord[0] *.9);
                searchObj.searchCoord[1] = (searchObj.mouseCoord[1] *.9);
            }
            searchObj.searchCoord[0]-= (searchObj.mouseCoord[0] - evt.x);
            searchObj.searchCoord[1]-= (searchObj.mouseCoord[1] - evt.y);
            searchObj.mouseCoord[0] = evt.x;
            searchObj.mouseCoord[1] = evt.y;
            this.style.left = searchObj.searchCoord[0]+"px";
            this.style.top = searchObj.searchCoord[1]+"px";
        }
    },
    searchBodymD:function(){
        searchObj.bodyClick = true;
    },
    searchBodymU:function(){
        searchObj.bodyClick = false;
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
        //Check to see if anything can be compared or viewed:
        for(let i=0;i<this.rankData.length;i++){
            for(let j=0;j<this.rankData[i][0].length;j++){
                if(this.rankData[i][1][j]){
                    searchViewBtn.disabled = false;
                    if(this.rankData[i][0][j] == "stats")
                        foundStats = true;
                    else foundRegular = true;
                }
                if(foundRegular && foundStats)
                    break;
            }
        }
        if(foundStats && foundRegular){
            searchCompareBtn.disabled = true;
            searchCompareBtn.parentElement.href = "#";
        }
        else if(foundStats || foundRegular)
            searchCompareBtn.disabled = false;

        //If we're on another page besides the modelTiming viewer, let's immediately create a clickable link in the buttons:
        if(onMtPage){
            searchViewBtn.onclick = ()=>{searchObj.doAction()};
            searchCompareBtn.onclick = ()=>{searchObj.doAction(true)};
        }
        else this.doAction();
    },
    doAction:function(compToggle = false){
        searchObj.doComparison = compToggle;
        //Scan through everything and dump it into a url. If we're on the modelTiming webpage, it will be separate calls to the server instead:
        if(onMtPage){
            document.getElementsByClassName("searchMenu")[0].style.display="none";
            animate();
            searchViewBtn.parentElement.href="#";
            searchCompareBtn.parentElement.href="#";
            for(let i=0;i<searchObj.rankData.length;i++){
                for(let j=0;j<searchObj.rankData[i][0].length;j++){
                    if(searchObj.rankData[i][1][j]){
                        getExperiment(searchObj.searchData[i].expid,searchObj.rankData[i][0][j],(i == searchObj.lastRankIndex[0] && j == searchObj.lastRankIndex[1])?searchObj.postAction:false);
                    }
                }
            }
        }
        else{
            searchViewBtn.onclick = undefined;
            searchCompareBtn.onclick = undefined;
            let totalString = "https://pace.ornl.gov/dev2/mt/";
            let expStr = "";
            let rankStr = "";
            for(let i=0;i<searchObj.rankData.length;i++){
                for(let j=0;j<searchObj.rankData[i][0].length;j++){
                    if(searchObj.rankData[i][1][j]){
                        let lastRank = (i == searchObj.lastRankIndex[0] && j == searchObj.lastRankIndex[1]);
                        expStr+=searchObj.searchData[i].expid+(lastRank?"":",");
                        rankStr+=searchObj.rankData[i][0][j]+(lastRank?"":",");
                    }
                }
            }
            totalString+=expStr+"/"+rankStr+"/";
            searchViewBtn.parentElement.href=totalString;
            searchCompareBtn.parentElement.href=totalString+"compare/";
        }
    },
    postAction:function(){
        expDownloadDefault();
        if(searchObj.doComparison){
            compList = [];
            expList.forEach(element=>{
                compList.push([element,0]);
            });
            comparisonMode.new(compList);
            comparisonMode.start();
        }
    }
}
//onchange is strange when bootstrap is involved, so here's an elaborate keydown instead :P
searchBar.onkeydown = evt=>{if(evt.key == "Enter") searchObj.listenerStop(evt);};
searchButton.onclick = searchObj.listenerStop;