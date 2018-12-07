//Author: Zachary Mitchell
//Purpose: The logic for the search page. This is a heavy modification of quickSearch.js designed for full screen usage.
var searchObj = {
    limit:10,
    searchData:[],
    rankData:[],
    lastRankIndex:[0,0],
    afterFunctions:[],
    search:function(searchStr,limit = this.limit,afterFunc,orderBy,ascDsc=false){
        console.log("%cHELLOOO!!","font-size:175%"); //This is VERY important part of the function.
        searchBody.innerHTML="";
        if(afterFunc)
            this.afterFunctions.push(afterFunc);
        //compile short names before searching:
        //This is here until shortcuts are implemented server-side
        /*if(/:/.test(searchStr)){
            let termArray = searchStr.split(" ");
            let elementList = [];
            termArray.forEach(element=>{
                elementList.push(element.split(":"));
            });
            delete termArray;
            //Scan through all element shortcuts:
            searchObj.expVars.forEach(expVar=>{
                if(expVar[2]){
                    elementList.forEach(element=>{
                        if(element[0] == expVar[2])
                            element[0] = expVar[1];
                    });
                }
            });
            //Re-compile:
            searchStr = "";
            elementList.forEach( (element,index)=>{
                searchStr+=(index>0?" ":"")+element.join(":");
            });
        }*/
        $.get(detectRootUrl()+"ajax/search/"+searchStr.replace(" ","+")+"/"+limit+(orderBy?"/"+orderBy+"/"+(ascDsc?"asc":"desc"):""),(data)=>{
        let resultData = JSON.parse(data)
        this.searchData = resultData[0];
        this.rankData = resultData[1];
        //First and foremost, lets organize the data; if we find anything related to "stats" or "0", we place those up front:
        this.rankData.forEach(element=>{
            for(let i=0;i<element[0].length;i++){
                if(element[0][i] == "stats" || element[0][i] == "0"){
                    for(let j=0;j<element[0].length;j++){
                        if(!(element[0][j] == "stats" || element[0][j] == "0")){
                            let temp = element[0][j];
                            element[0][j] = element[0][i];
                            element[0][i] = temp;
                            break;
                        }
                    }
                }
            }
            //Now, prioritize the stats variable so it's always on top:
            if(element[0][0] == "0" && element[0][1] && element[0][1] == "stats"){
                let temp = element[0][0];
                element[0][0] = element[0][1];
                element[0][1] = temp;
            }
        }
        );
        this.searchData.forEach( (element,index) => {
            let searchResult = document.createElement("tr");
            searchResult.className = "searchItem";
            searchResult.value = index;
            this.expVars.forEach(val=>{
                if(val[3]!==false){
                    switch(val[1]){
                        case "expid":
                        searchResult.innerHTML+="<td onclick='searchObj.expDetails("+element.expid+")'><a href='"+detectRootUrl()+"exp-details/"+element.expid+"' title='Click here for more details.'>"+element.expid+"</a></td>";
                        break;
                        case "compset":
                        case "user":
                        case "machine":
                        searchResult.innerHTML+="<td onclick='if(arguments[0].target == this)searchObj.expDetails("+element.expid+")'><a class='searchLink' href='"+detectRootUrl()+"search/"+val[1]+":"+element[val[1]]+"'>"+element[val[1]].substr(0,20)+(element[val[1]].length > 20?"...":"")+"</a></td>";
                        break;
                        default:
                        searchResult.innerHTML+="<td onclick='searchObj.expDetails("+element.expid+")'>"+element[val[1]].substr(0,20)+(element[val[1]].length > 20?"...":"")+"</td>";
                    }
                }
            });
            let checkStr = "<td>";
            let checkMoreStr = "<div><div style='display:none' class='moreContainer'>";
            let foundMore = false;
            searchObj.rankData[index][0].forEach( rank=>{
                outputStr= "<input type='checkbox' onchange='searchObj.scanChecks()' style='margin-right:3px'/><a href='"+detectRootUrl()+"summary/"+element.expid+"/"+rank+"' title='View this experiment.'><b>"+rank+"</b></a></br>"; 
                if(rank == "stats" || rank == "0")
                    checkStr+=outputStr;
                else {
                    checkMoreStr+=outputStr;
                    foundMore = true;
                }
            });
            checkMoreStr+="</div><button onclick='searchObj.moreClick(this.parentElement);' class='btn-sm btn-outline-dark' style='margin-top:3px'>More</button></div>"
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
    //Scans all checkboxes to turn on the comparison and view buttons accordingly.
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
        let rankCount = 0;
        //Check to see if anything can be compared or viewed:
        for(let i=0;i<this.rankData.length;i++){
            for(let j=0;j<this.rankData[i][0].length;j++){
                if(this.rankData[i][1][j]){
                    this.disableBtn("searchViewBtn",false);
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
            this.disableBtn("searchCompareBtn",true);
            this.disableBtn("searchFlameBtn",true);
        }
        else if(foundStats || foundRegular){
            this.disableBtn("searchCompareBtn",rankCount > 1?false:true);
            this.disableBtn("searchViewBtn",false);
        }
        else{
            this.disableBtn("searchCompareBtn",true);
            this.disableBtn("searchViewBtn",true);
        }
        //Flame button:
        if(foundStats || !foundRegular)
            this.disableBtn("searchFlameBtn",true);
        else if(foundRegular)
            this.disableBtn("searchFlameBtn",false);

        //AtmBtn:
        this.disableBtn("searchAtmBtn",foundStats && !foundRegular?false:true);
        

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
        if(!searchAtmBtn.disabled) searchAtmBtn.parentElement.href = totalString.replace("summary/","atmos/") + expStr;
        totalString+=expStr+"/"+rankStr+"/";
        if(!searchViewBtn.disabled) searchViewBtn.parentElement.href=totalString;
        if(!searchCompareBtn.disabled) searchCompareBtn.parentElement.href=totalString+"compare/";
        if(!searchFlameBtn.disabled) searchFlameBtn.parentElement.href = totalString.replace("summary/","flamegraph/");
    },
    moreClick:function(element){
        let more = element.getElementsByClassName("moreContainer")[0];
        let button = element.getElementsByTagName("button")[0];
        $(more).slideToggle("fast");
        button.innerHTML = (button.innerHTML == "More"?"Less":"More");

    },
    disableBtn:function(btnString,tf){
        srcBtn = document.getElementById(btnString);
        srcBtn.disabled = tf;
        if(tf) srcBtn.parentElement.href = "";
        srcBtn.className = (tf?"btn btn-primary btn-dark":"btn btn-primary btn-success");
    },
    expDetails:(expid)=>{
        location.assign(detectRootUrl()+"exp-details/"+expid);
    },
/*The table values are right here so they don't have to be repeated.
Index definitions:
0: Display name
1: internal name
2: short name
3: display this value (true by default)
4: additional html (can be left blank)*/
    expVars:[
    	["ID","expid"],
    	["User","user"],
    	["Machine","machine"],
    	["Compset","compset","comp"],
    	["Res","res"],
    	["Case","case"],
    	["Total PEs","total_pes_active","pes"],
    	["Run Length","run_length","run",true,`<br><span style="font-size:75%">(days)</span>`],
        ["Throughput","model_throughput","through",true,`<br><span style="font-size:75%">(sim_years/day)</span>`],
        ["Init time","init_time"],
    	["ExpDate","exp_date","date"]
    ],
}
