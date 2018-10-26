//Author: Zachary Mitchell
//Purpose: The javaScript for search.html. Moved here due to the large size.

window.onresize = ()=>{
	if(window.innerWidth < 1060)
		document.getElementsByClassName("pTextMenu")[0].style.width = "76%";
	else if(window.innerWidth > 1060)
		document.getElementsByClassName("pTextMenu")[0].style.width="42em";
}

//getDistinct should only be flagged to true when in a search page (not the home page), so the template assumes accordingly...
function searchAndCheck(sq = searchQuery ){
	searchObj.search(sq,searchObj.limit,()=>{
	if(searchObj.searchData.length == searchObj.limit){
	 searchObj.limit*=2;
	}
	else moreBtn.style.display = "none";

	},orderBySelect.children[orderBySelect.selectedIndex].value,ascCheck.checked);
	let newLink = detectRootUrl() +(sq == "*"?"":"search/"+sq);
	if(newLink != window.location.href)
	
		history.pushState("","",newLink);
	sSummaryLink.href=detectRootUrl()+"searchSummary/"+sq;

	if(sq!="*")
		homeSearchBar.value = sq;
}

//predictive search + home search functionality:
homeSearchPredict = new predictiveSearch.element(homeSearchBar,"hsb");
homeSearchBar.onkeydown = evt=>{
	if(evt.key == "Enter" && homeSearchPredict.allowEnter){
		searchObj.limit = 10;
		if(homeSearchBar.value!='') searchAndCheck(homeSearchBar.value);
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
	searchObj.search((homeSearchBar.value!=''?homeSearchBar.value:'*'),searchObj.limit,undefined,orderBySelect.children[orderBySelect.selectedIndex].value,ascCheck.checked)
}

$(document).ready(function(){
	window.onresize();
	searchAndCheck();
	/*$("#expTable").tablesorter({
		widthFixed: false
		});*/
});