//Author: Zachary Mitchell
//Purpose: A fun loading screen for PACE! This may or may not be needed, depending on the size of the JSON we load... (P.S, HI SARAT + GARUAB + RANDOM PERSON!!!)
//What we're going for here is an html-free way to load these elements & play with them without directly writing inside modelTiming.html...
//load the images:
var barImg = [];
var barTd=[];
var barPercent=[[25,false],[50,false],[75,false],[100,false]];
var barInterval;
["P","R","B","G"].forEach((letter,index)=>{
    barImg[index] = document.createElement("img");
    barTd[index] = document.createElement("td");
    barImg[index].src="../static/img/bar"+letter+".png";
    barImg[index].style.width="100%";
    barTd[index].appendChild(barImg[index]);
});

//Stylesheet for fading in & out:
lsFade = document.createElement("style");
lsFade.innerHTML=`
.loadScreen{
  position:absolute;
  top:0px;
  width:100%;
  height:100%;
  background-color:white;
  animation: fadeIn .3s;
}
@keyframes fadeIn{
    from{opacity:0;}
    to{opacity:1;}
}`;
//The load-screen background:
lsBackground = document.createElement("div");

lsBackground.className="loadScreen";
lsBackground.innerHTML="<table style='margin-top:25%;margin-left:25%'><tbody><tr id='lsTableRow'></tr></tbody></table>";

barTd.forEach((element)=>{
    lsBackground.getElementsByTagName("tr")[0].appendChild(element);
});

function moveBar(index,speed){
    if(barPercent[index][1]){
        barPercent[index][0]+=speed;
    }
    else{
        barPercent[index][0]-=speed;
    }
    barImg[index].style.height = barPercent[index][0] + "%";
    barImg[index].style.marginTop = (100 - barPercent[index][0]*1.5) + "%";
    if(barPercent[index][0] >= 100 && barPercent[index][1])
        barPercent[index][1] = false;
    else if(barPercent[index][0] <= 0 && !barPercent[index][1])
        barPercent[index][1] = true;
}

function animate(tf=true,speed=10){
    if(tf){
        function newInterval(){
            barInterval = setInterval( (()=>{moveBar(0,speed);moveBar(1,speed);moveBar(2,speed);moveBar(3,speed)}),16.6);
        }
        if(!barInterval){
            document.body.appendChild(lsFade);
            document.body.appendChild(lsBackground);
            newInterval();
        }
        else{
            clearInterval(barInterval);
            newInterval();
        }
    }
    else{
        clearInterval(barInterval);
        document.body.removeChild(lsBackground);
        barInterval = undefined;
    }
}