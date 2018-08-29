//Author: Zachary Mitchell
//Purpose: create a querying interface for the search bar! This should pull up any relavent experiments; if one is selected, you can choose to view/compare it.
var searchObj = {
    searchdata:[],
    search:function(searchStr,limit = 20){
        console.log("HI SARAAAAT!");
        $.get("https://pace.ornl.gov/dev2/ajax/search/"+searchStr.replace(" "+"+")+"/"+limit,(data)=>{
            this.searchdata = JSON.parse(data);
            console.log(this.searchdata);
            //Generate the search page object:
            let resultPage = document.createElement("div");
            resultPage.className = "searchMenu";
            let resultBody = document.createElement("div");
            resultBody.className = "searchBody";
            this.searchdata.forEach(element => {
                let searchResult = document.createElement("div");
                searchResult.className = "searchItem";
                searchResult.innerHTML+="<h4>"+element.expid+"</h4>User: "+element.user+"</h3><br>Machine:"+element.machine;
                resultBody.appendChild(searchResult);
            });
            resultPage.appendChild(resultBody);
            resultPage.innerHTML+="<button disabled>compare</button><button disabled>View</button>";
            document.body.appendChild(resultPage);
        });
    },
    //Tames the beast known as bootstrap:
    listenerStop:function(evt){
        evt.preventDefault();
        searchObj.search(searchBar.value);
    }
}
//onchange is strange when bootstrap is involved, so here's an elaborate keydown instead :P
searchBar.onkeydown = evt=>{if(evt.key == "Enter") searchObj.listenerStop(evt);};
searchButton.onclick = searchObj.listenerStop;