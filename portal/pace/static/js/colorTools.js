//Author: Zachary Mitchell
//Purpose: These originally come from modelTiming.js; they're designed to help make colors easier.

//return an rgb-based color string based on a percentage provided by the user:
function percentToColor(percentage=50,transparency=false,returnType=0,colors=[[0,0,255],[0,255,0],[255,0,0]]){
    if(percentage > 100)
        percentage=100;
    let subtractValue = 100 / (colors.length-1);
    let difference = 0;//This will represet a certain percentage of subtractValue.
    let colorIndex=0; //The color we will be transitioning from.

    //Add up the subtract values until we have one that's greater than (or matches) the percentage:
        for(let i=0;i<colors.length;i++){
            if(percentage >= subtractValue * i){
                colorIndex = i;
                difference = (subtractValue * (i+1) ) - percentage;
            }
            else break;
        }
    let resultColor=colors[colorIndex].slice();
    let colorPercent = .01 * ( (100 / subtractValue) * (subtractValue-difference));
    if(percentage!=100){
        for(let i=0;i<resultColor.length;i++){
            resultColor[i]-=Math.floor( (resultColor[i] - colors[colorIndex+1][i]) * colorPercent );
        }
    }
    //This value is optional; if returnType is > 0, you optionally get the raw values as well.
    let resultColorString;
    if(returnType!=1)
        resultColorString = "rgba("+resultColor[0]+","+resultColor[1]+","+resultColor[2]+","+(transparency?transparency:1)+")";
    return (returnType == 0?resultColorString:returnType==1?resultColor:[resultColorString,resultColor]);
}

//Grabs the ratio of all values inserted, and compares them.
function arrayToPercentages(arrayIn,rankMode = false){
    let ratioVals=[];
    //Default mode:
    if(!rankMode){
        //Compare the node count, find the largest, and make percentages based off of those numbers
        let biggestNumber = 0;
        arrayIn.forEach(element=>{
            if(element > biggestNumber)
                biggestNumber = element;
        });
    
        arrayIn.forEach(element=>ratioVals.push((100/biggestNumber)*element))
    }
    else{
        //Percentages are based on what order the values in the given array would be in. (e.g from 1-3: 3 == 99% 1 == 33% 2 == 66%)
        let indexArray = [];
        arrayIn.forEach( (element,index)=>indexArray.push([element,index]));
        //Sort numbers from greatest to least:
        indexArray.sort((a,b)=>a[0]>b[0]);
        //Create new percentages:
        let basePercent = 100/indexArray.length;
        indexArray.forEach( (element,index) =>{
            ratioVals[element[1]] = basePercent*(index+1);
        });
    }
    return ratioVals;
}