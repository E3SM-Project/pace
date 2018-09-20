//Author: Zachary Mitchell
//Purpose: Create a predictive search input system! This retreives information from the database first, then disects every single movement of the user to insert that predicted text.

var predictiveSearch = {
    //Predictive-Search-Pool (psp ;P): a place where all predictive search objects live:
    //This helps to trace back element variables
    pool:[],
    //The key object of this file.
    element:function(targetInput,id){
        //This helps us figure out if the context we're talking about is this object (not an html tag)
        this.targetId = id;
        this.targetIn = targetInput;
        this.targetParent = (targetInput.parentElement.tagName == "BODY" || targetInput.parentElement.tagName == "HTML"? document.body:targetInput.parentElement);
        
        this.pTextMenu = document.createElement("div");
        this.ptmValues = ["thing","ror","supercalifragilisticexpialidocious","MrSarat"];
        this.pTextMenu.className = "pTextMenu";
        this.targetParent.appendChild(this.pTextMenu);
        //Event Listeners:
        this.keydownListener = evt=>{
            if(evt.key == "Down" || evt.key == "Up"){
                evt.preventDefault();
            }
            //if(targetIn.selectionStart!=0 && targetIn.value[targetIn.selectionStart]=="")
            //Load the results inside the textMenu:
            console.log(this.targetIn.value[this.targetIn.selectionStart]);
            this.pTextMenu.innerHTML = "";
            this.ptmValues.forEach(element => {
                this.pTextMenu.innerHTML+="<div>"+element+"</div>";
            });
            this.pTextMenu.style.display="";
        };
        predictiveSearch.pool[id] = this;
    },
}