//Author:Zachary Mitchell
//Purpose: This function is useful enough that it would work well across multiple pages on this site:

/*As of right now, our personal usage doesn't rely on this anymore, since we have personal subdomains.
In the past however, this was a way to help detect if our url looked something like: pace.ornl.gov/dev2/foo/bar.
If you're launching this on a new server, and you need the above url layout, change the regex below (marker) to suit your needs.*/

//Find the url needed based based on the given marker:
function detectRootUrl(srcUrl = document.URL,defaultIndex = 3, marker = /dev[0-9]/){
    let splitUrl = srcUrl.split("/");
    let resultStr = "";
    let index = 0;
    let foundMarker = false;
    //If the regex shows up, the url will be up to that associated index; otherwise the root url is defaultIndex. (As of this writing, after https and the website name)
    while(!marker.test(splitUrl[index]) && index<=splitUrl.length)
        index++;
    //Generate the URL:
    if(marker.test(splitUrl[index]))
        foundMarker = true;
    else index = defaultIndex;
    for(let i=0;i<index;i++){
        resultStr+=splitUrl[i]+"/";
    }
    if(foundMarker)
        resultStr+=splitUrl[index]+"/";
    return resultStr;
}