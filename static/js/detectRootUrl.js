//Author:Zachary Mitchell
//Purpose: This function is useful enough that it would work well across multiple pages on this site:
function detectRootUrl(marker = "mt"){
    splitUrl = document.URL.split("/");
    resultStr = "";
    index = 0;
    while(splitUrl[index]!=marker){
        resultStr+=splitUrl[index]+"/";
        index++;
    }
    return resultStr;
}