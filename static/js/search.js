//Author: Zachary Mitchell
//Purpose: The logic for the search page. This is a heavy modification of quickSearch.js designed for full screen usage.
var searchObj = {
    limit:20,
    searchData:[],
    rankData:[],
    lastRankIndex:[0,0],
    doComparison:false,
    afterFunctions:[],
    search:function(searchStr,limit = this.limit,afterFunc){
        console.log("HI SARAAAAT!");
        searchBody.innerHTML="";
        this.afterFunctions.push(afterFunc);
        $.get(detectRootUrl()+"/ajax/search/"+searchStr.replace(" ","+")+"/"+limit,(data)=>{
        let resultData = JSON.parse(data)
        this.searchData = resultData[0];
        this.rankData = resultData[1];
        //First and foremost, lets organize the data; if we find anything related to "stats" or "0", we place those up front:
        this.rankData.forEach(element=>{
            for(let i=0;i<element[0].length;i++){
                if(element[0][i] == "stats" || element[0][i][0] == "0"){
                    for(let j=0;j<element[0].length;j++){
                        if(!(element[0][j] == "stats" || element[0][j][0] == "0")){
                            let temp = element[0][j];
                            element[0][j] = element[0][i];
                            element[0][i] = temp;
                            break;
                        }
                    }
                }
            }
        });
        this.searchData.forEach( (element,index) => {
            let searchResult = document.createElement("tr");
            searchResult.className = "searchItem";
            searchResult.value = index;
            searchResult.innerHTML+="<td><a href='"+detectRootUrl()+"exp-details/"+element.expid+"' target='_blank' title='Click here for more details.'>"+element.expid+
            "</a></td><td>"+element.user+"</td>"+
            "<td>"+element.machine+"</td>"+
            "<td>"+element.total_pes_active+"</td>"+
            "<td>"+element.run_length+"</td>"+
            "<td>"+element.model_throughput+"</td>"+
            "<td>"+element.mpi_tasks_per_node+"</td>"+
            "<td>"+element.compset+"</td>";
            let checkStr = "<td>";
            let checkMoreStr = "<div><span onclick='searchObj.moreClick(this.parentElement)' style='font-weight:bold;'>More</span><div style='display:none' class='moreContainer'>";
            let foundMore = false;
            searchObj.rankData[index][0].forEach( rank=>{
                outputStr= "<a href='"+detectRootUrl()+"summary/"+element.expid+"/"+rank+"' title='View this experiment.'><b>"+rank+"</b></a><input type='checkbox' onchange='searchObj.scanChecks()'/></br>"; 
                if(rank == "stats" || rank[0] == "0")
                    checkStr+=outputStr;
                else {
                    checkMoreStr+=outputStr;
                    foundMore = true;
                }
            });
            checkMoreStr+="</div></div>"
            searchResult.innerHTML+=checkStr+(foundMore?checkMoreStr:"")+"</td>";
            searchBody.appendChild(searchResult);
        });
        //Generate the search page object:
        searchViewBtn.disabled = true;
        searchCompareBtn.disabled = true;

        //Execute any functions that are in the list for que:
        if(searchObj.afterFunctions.length > 0){
            searchObj.afterFunctions.forEach(element=>{
                element();
            });
            searchObj.afterFunctions = [];
        }
        });
    },
    scanChecks:function(){
        let searchItems = document.getElementsByClassName("searchItem");
        for(let i=0;i<this.searchData.length;i++){
            let checkboxes = searchItems[i].getElementsByTagName("input");
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
        else{
            searchCompareBtn.disabled = true;
            searchViewBtn.disabled = true;
        }

        this.doAction();
    },
    doAction:function(compToggle = false){
        searchObj.doComparison = compToggle;
        //Scan through everything and dump it into a url.
        searchViewBtn.onclick = undefined;
        searchCompareBtn.onclick = undefined;
        let totalString = detectRootUrl()+"summary/";
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
    },
    moreClick:function(element){
        let more = element.getElementsByClassName("moreContainer")[0];
        more.style.display=(more.style.display == "none"?"":"none");
    }
}