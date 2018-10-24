//Author: Zachary Mitchell
//Purpose: The javaScript for search.html. Moved here due to the large size.

window.onresize = ()=>{
	if(window.innerWidth < 1060)
		document.getElementsByClassName("pTextMenu")[0].style.width = "76%";
	else if(window.innerWidth > 1060)
		document.getElementsByClassName("pTextMenu")[0].style.width="42em";
}

//getDistinct should only be flagged to true when in a search page (not the home page), so the template assumes accordingly...
function searchAndCheck(sq = searchQuery,matchMode = (getDistinct?true:false) ){
	searchObj.search(sq,searchObj.limit,()=>{
	if(searchObj.searchData.length == searchObj.limit){
	 searchObj.limit*=2;
	}
	else moreBtn.style.display = "none";

	//This is experimental:
	//Each link gets some special treatment so the user stays on the same page while browsing:
	/*[...document.getElementsByClassName("searchLink")].forEach(link=>{
		link.onclick = evt=>{
			evt.preventDefault();
			matchModeCheck.checked = true;
			searchAndCheck(evt.target.href.split("advsearch/")[1],true);
		}
	});*/

	},matchMode,orderBySelect.children[orderBySelect.selectedIndex].value,ascCheck.checked);
	let newLink = detectRootUrl() +(sq == "*"?"":(matchMode?"advsearch/":"search/")+sq);
	if(newLink != window.location.href)
		history.pushState("","",newLink);

	if(sq!="*")
		homeSearchBar.value = sq;
}

matchModeCheck.onclick = function(){
	homeSearchBar.value="";
	homeSearchBar.placeholder = (this.checked?"user:name machine:platform colname:value ...":"Keyword");
	if(homeSearchBar.innerHTML.replace(" ","")!="")
		searchAndCheck(homeSearchBar.value,matchModeCheck.checked);
	//catRefButton.style.display = (catRefButton.style.display == "none"?"":"none");
	//catReference.style.display = "none";
	homeSearchPredict.enabled = !matchModeCheck.checked;
}

//predictive search + home search functionality:
homeSearchPredict = new predictiveSearch.element(homeSearchBar,"hsb");
homeSearchBar.onkeydown = evt=>{
	if(evt.key == "Enter" && homeSearchPredict.allowEnter){
		searchObj.limit = 10;
		if(homeSearchBar.value!='') searchAndCheck(homeSearchBar.value,matchModeCheck.checked);
	}
	homeSearchPredict.keydownListener(evt);
};
homeSearchBar.onkeyup = evt=>{
  homeSearchPredict.keyupListener(evt);
  if(homeSearchBar.value!="" && homeSearchPredict.enabled)
      $.get(detectRootUrl()+"ajax/similarDistinct/"+homeSearchPredict.inputWords[homeSearchPredict.wordIndex],data=>homeSearchPredict.refreshKeywords(JSON.parse(data)));
}
homeSearchBar.onblur = ()=>setTimeout(()=>predictiveSearch.menuBlur("hsb"),150);

//Generate the refernece table:
searchObj.expVars.forEach( (element,index)=>{
	catReference.innerHTML+=(index > 0?"<br>":"")+"<b>"+element[0]+"</b> = "+(element[2]?element[2]:element[1]);
});

//Generate the table head:
var tHead = expTable.getElementsByTagName("thead")[0].children[0];
searchObj.expVars.forEach(element=>{
	if(element[3] === undefined || element[3] === true)
		tHead.innerHTML+="<th>"+element[0]+(element[4]!=undefined?element[4]:"")+"</th>";
});
tHead.innerHTML+="<th>Summary Charts</th>";
delete tHead;

//Generate order by selection:
searchObj.expVars.forEach(element=>{
	orderBySelect.innerHTML+="<option value='"+element[1]+"'>"+element[0]+"</option>";
});

function sortOrderToggle(){
	searchObj.search((homeSearchBar.value!=''?homeSearchBar.value:'*'),searchObj.limit,undefined,matchModeCheck.checked,orderBySelect.children[orderBySelect.selectedIndex].value,ascCheck.checked)
}

$(document).ready(function(){
	window.onresize();
	searchAndCheck();
	/*$("#expTable").tablesorter({
		widthFixed: false
		});*/
});