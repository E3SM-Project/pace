//Author: Zachary Mitchell
//Purpose: Create a predictive search input system! This retreives information from the database first, then disects every single movement of the user to insert that predicted text.

var predictiveSearch = {
    //Predictive-Search-Pool (psp ;P): a place where all predictive search objects live:
    //This helps to trace back element variables
    pool:[],
    keyBlackList:["ArrowUp","ArrowDown","Enter","Escape","Control","Shift"," ","Tab"],
    //The key object of this file.
    element:function(targetInput,id){
        //This helps us figure out if the context we're talking about is this object (not an html tag)
        this.targetId = id;
        this.targetIn = targetInput;
        this.allowEnter = true;
        //This detects where we are in the selection menu.
        this.highlightIndex;
        this.pTextMenu = document.createElement("div");
        this.ptmValues = [];
        this.pTextMenu.className = "pTextMenu";
        (targetInput.parentElement.tagName == "BODY" || targetInput.parentElement.tagName == "HTML"? document.body:targetInput.parentElement).appendChild(this.pTextMenu);
        this.inputWords = [];
        this.wordIndex = 0;
        this.lastKeyPressed = "";
        this.enabled = true;
        //Event Listeners:
        this.keydownListener = evt=>{
            if (this.enabled){
                if(this.targetIn.value == "")
                    this.pTextMenu.style.display="none";
    
                if(evt.key == "ArrowDown" || evt.key == "ArrowUp"|| evt.key == "Tab" || (evt.key == "Enter" && !this.allowEnter) ){
                    evt.preventDefault();
                }
                //This didn't look organized as a regular if statement XP
                //Apply the predictive text depending on your key, also remove the searchDiv:
                switch(evt.key){
                    case "Tab":
                        if(this.highlightIndex === undefined)
                            this.highlightIndex = 0;
                    case "Enter":
                        if(this.targetIn.value!="" && this.pTextMenu.style.display!="none")
                            this.applyText();
                        this.allowEnter = true;
                    case "Escape":
                    case " ":
                    this.pTextMenu.style.display="none";
                }
                if( (evt.key == "ArrowDown" || evt.key == "ArrowUp") && this.pTextMenu.style.display!="none" && this.ptmValues.length > 0){
                    this.allowEnter = false;
                    this.pTextMenu.children[this.highlightIndex].style.backgroundColor = "";
                    this.highlightIndex = (evt.key == "ArrowDown"? this.highlightIndex+1:this.highlightIndex-1);
                    if(this.highlightIndex == this.ptmValues.length)
                        this.highlightIndex--;
                    else if(this.highlightIndex < 0)
                        this.highlightIndex++;
                    this.pTextMenu.children[this.highlightIndex].style.backgroundColor = "lightgray";
                }
            }
        };
        this.keyupListener = evt=>{
            if(this.enabled){
                this.lastKeyPressed = evt.key;
                //Proccess all words, and detect which word the cursor is on:
                //This wound up being here instead of keydown because of an accuracy glitch: on the keydown, it wouldn't show the latest index being used. This was cruicial for detecting which word the user is on.
                this.inputWords = this.targetIn.value.split(" ");
                //Go through each word to figure out where the user is
                let totalStr = 0;
                this.wordIndex = 0;
                while(totalStr< this.targetIn.selectionStart){
                    totalStr+=this.inputWords[this.wordIndex].length+1;
                    if(totalStr< this.targetIn.selectionStart)
                        this.wordIndex++;
                }
                if(this.targetIn.value[totalStr] == " "){
                    this.wordIndex++;
                }
                // console.log("word: "+this.inputWords[this.wordIndex]);
                // console.log(this.targetIn.selectionStart);
            }
        }
        this.refreshKeywords = wordArray=>{
            this.ptmValues = wordArray;
            //Load the results inside the textMenu:
            if(!predictiveSearch.keyBlackList.find(element=>{return element == this.lastKeyPressed})){
                //Refresh the menu:
                if(this.pTextMenu.length == 0)
                    this.pTextMenu.style.display == "none";
                else{
                    this.pTextMenu.innerHTML = "";
                    this.highlightIndex = undefined;
                    this.ptmValues.forEach( (element,index) => this.pTextMenu.innerHTML+="<div data-index="+index+" onmouseover='predictiveSearch.highlight(this,\""+this.targetId+"\")' onmouseout='predictiveSearch.unHighlight(this,\""+this.targetId+"\")' onclick='this.parentElement.style.display=\"none\";predictiveSearch.pool[\""+this.targetId+"\"].applyText()'>"+element+"</div>");
                    this.pTextMenu.style.display="block";
                    if(this.ptmValues.length > 0){
                        this.highlightIndex = 0
                        this.pTextMenu.children[this.highlightIndex].style.backgroundColor = "lightgray";
                    }
                }
            }
        }
        this.applyText = function(){
            //Re-create the user's string based on user position:
            //Not sure why this would ever happen, but the if-statement is here just in case...
            if(this.ptmValues.length >0){
                this.inputWords[this.wordIndex] = this.ptmValues[this.highlightIndex];
                this.targetIn.value = this.inputWords.join(" ");
                this.targetIn.focus();
            }
        }
        predictiveSearch.pool[id] = this;
    },
    //These two functions are for mouse listeners:
    highlight:function(element,poolId){
        this.pool[poolId].highlightIndex = element.dataset.index;
        element.style.backgroundColor = "lightgray";
    },
    unHighlight:function(element,poolId){
        this.pool[poolId].highlightIndex = undefined;
        element.style.backgroundColor = "";
    },
    menuBlur:function(poolId){
        this.pool[poolId].pTextMenu.style.display = "none";
    }
}