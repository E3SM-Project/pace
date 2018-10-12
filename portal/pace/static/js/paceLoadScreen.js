//Author: Zachary Mitchell
//Purpose: A fun loading screen for PACE! This may or may not be needed, depending on the size of the JSON we load... (P.S, HI SARAT + GARUAB + RANDOM PERSON!!!)
//What we're going for here is an html-free way to load these elements & play with them without directly writing inside modelTiming.html...
//load the images:
var chartBars = [];
var barInterval;

//Bar object: a simple object to keep track of each bar's values
function chartBar(src,percent, upDown=false,speed = 10){
    this.img = document.createElement("img");
    this.img.src=src;
    this.percent = percent;
    this.upDown = upDown;
    this.speed = speed;
    this.move = function(movingSpeed = this.speed){
        if(this.upDown){
            this.percent+=movingSpeed;
        }
        else{
            this.percent-=movingSpeed;
        }
        if(this.percent >= 100 && this.upDown)
            this.upDown = false;
        else if(this.percent <= 0 && !this.upDown)
            this.upDown = true;
    }
}

["P","R","B","G"].forEach((letter,index)=>{
    chartBars.push(new chartBar("/static/img/bar"+letter+".svg", 100-(20 * (index+1 )) ));
});

//Stylesheet for fading in & out:
lsFade = document.createElement("style");
lsFade.innerHTML=`
.loadScreen{
  position:absolute;
  top:0px;
  animation: fadeIn .3s;
  background-color:white;
  z-index:10;
}
@keyframes fadeIn{
    from{opacity:0;}
    to{opacity:1;}
}`;

lsBackground = document.createElement("canvas");
lsBackground.className="loadScreen";
var lsContext = lsBackground.getContext("2d");
//Due to technical limitations, I can't directly implement a listener for this load screen, but I can provide it!
//This can rest inside a window.onresize function.
var paceLoadResize = function(){
    lsBackground.width=window.innerWidth;
    lsBackground.height=window.innerHeight;
    lsDraw();
}

//Animate the bars!
function lsDraw(){
    lsContext.clearRect(0,0,window.innerWidth,window.innerHeight);
    let currX = (window.innerWidth/2) - ( chartBars[0].img.width * (chartBars.length / 2) );
    let sizeMod = 100;
    //Resize the charts if they don't fit:
    /*if( window.innerWidth*.6 < chartBars[0].img.width*chartBars.length )
        sizeMod*= 100;*/
    //render each bar based on the resolution:
    chartBars.forEach((element)=>{
        //Firefox is a special snowflake, so transforming is disabled there :/
        //got this from https://stackoverflow.com/questions/9847580/how-to-detect-safari-chrome-ie-firefox-and-opera-browser :
        let transform = typeof InstallTrigger == 'undefined';
        lsContext.setTransform(1,0,0,1,0,(100-(element.percent * 2) ));
        lsContext.drawImage(element.img,currX,window.innerHeight/2,element.img.width,element.img.height * (transform? (element.percent *.01):1) );
        currX+=element.img.width;
    });
}

function animate(tf=true,speed){
    if(tf){
        paceLoadResize();
        function newInterval(){
            barInterval = setInterval( (()=>{
                chartBars.forEach((element)=>{
                    element.move(speed);
                });
                lsDraw();
            }),16.6);
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