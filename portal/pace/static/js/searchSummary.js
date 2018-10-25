//Author: Zachary Mitchell
//Purpose: The javascript for searchSummary.html

//This is a wrapper for the actual chart made by chart.js. It makes it easier to group functions relative to this project.
var bChartObj = function(id,config){
    this.chart = new Chart(id,{
        type:"bubble",
        data: { datasets:[] },
        options: {}
    });

    //This makes it easier to map certain machines and their data. (No need for constant iterations)
    this.labelMap = {};
    this.idByLabel = {};

    //The configuration for this object; values can either be retrieved from the database, or hard-coded. use the second index in each array to toggle that option.
    //Values can also be functions! You can programatically control what values get used. The argument sent in is the object about to be displayed
    //The third index defines whether or not the value is safe to use while retreiving names of values from the database.
    //When writing outside the scope of the object, the context for grabbing values within the config object is "this.config";

    /*example function:
    
    r:[obj=>{
        console.log(obj[this.config.label[0]()]);
        return 15;
    },true]*/
    if(!config){
        this.config = {
            label:["machine"],
            x:["total_pes_active"],
            y:["model_throughput"],
            r:[15,true]
        }
    }

    this.click = evt=>{
        let evtVars = this.chart.getElementAtEvent(evt);
        if(evtVars[0])
            open(detectRootUrl()+"exp-details/"+this.idByLabel[this.chart.data.datasets[evtVars[0]._datasetIndex].label][evtVars[0]._index]);
    }
    document.getElementById(id).onclick = this.click;

    this.resetData= function(){
        this.chart.data = { datasets:[] };
        this.labelMap = {};
        this.idByLabel = {};
    }
    //Add data and refresh the chart. The same search syntax as the homepage's search bar applies to this query (basic & advanced searches work as normal).
    this.addData = function(query){
        //Make the list of items needed from the database:
        let dbValueStr = "expid";
        Object.keys(this.config).forEach(key=>{
            if(typeof(this.config[key][0]) == "function" && this.config[key][2])
                dbValueStr+=","+this.config[key][0]();
            else if(!this.config[key][1])
                dbValueStr+=","+this.config[key][0];
        });
        $.get(detectRootUrl()+"ajax/specificSearch/"+query+"/"+dbValueStr,data=>{
            resultData = JSON.parse(data);
            let newColors = false;
            resultData.forEach(obj=>{
                //Initialize config variables:
                let configData = {};
                Object.keys(this.config).forEach(key=>{
                    if(typeof(this.config[key][0]) == "function")
                        configData[key] = this.config[key][1]?this.config[key][0](obj):obj[this.config[key][0](obj)];
                    else configData[key] = this.config[key][1]?this.config[key][0]:obj[this.config[key][0]];
                });

                if(!this.labelMap[configData.label]){
                    this.labelMap[configData.label] = {data:[],label:configData.label};
                    this.idByLabel[configData.label] = [];
                    this.chart.data.datasets.push(this.labelMap[configData.label]);
                    newColors = true;
                }
                this.labelMap[configData.label].data.push({x:configData.x,y:configData.y,r:configData.r});
                this.idByLabel[configData.label].push(obj.expid);
            });
            if(newColors){
                //Convert letters into numbers, then convert them to percentages:
                let labelNumbers = [];
                Object.keys(this.labelMap).forEach( (key,index)=>{
                    labelNumbers[index] = 0;
                    for(let i = 0;i<key.length;i++){
                        labelNumbers[index]+=key.charCodeAt(i);
                    }
                });
                let percentages = arrayToPercentages(labelNumbers,true);
                //Insert colors:
                Object.keys(this.labelMap).forEach((key,index)=>{
                    this.labelMap[key].backgroundColor = percentToColor(percentages[index],0.2);
                });
            }

            this.chart.update();
        });
    }
}