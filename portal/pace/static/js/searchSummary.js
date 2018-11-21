//Author: Zachary Mitchell
//Purpose: The javascript for searchSummary.html

var queryHistory = [];
var bubbleRadius = 15;
var bubbleGrow = true;
Chart.defaults.global.defaultFontSize = 16;
//This is a wrapper for the actual chart made by chart.js. It makes it easier to group functions relative to this project.
var bChartObj = function(id,config){

    //This makes it easier to map certain machines and their data. (No need for constant iterations)
    this.labelMap = {};
    this.idByLabel = {};

    /*The configuration for this object:
    When writing outside the scope of this object, the context for grabbing values within the config object is "this.config"

    configuration options:
        val: the target value. This can either be a variable name for the database, a raw value or even a function!
        hardCoded: (bool) specifies whether to use this value as-is, or as a key in the queried data.
        dbFriendly: (bool) this can be toggled on if this value is a function & safe for generating queries.
        labelName: (x and y only) These are the nicknames for x and y. They get displayed on the chart as alternatives to the full name.
    
    example function:
    r:{val:obj=>{
        console.log(obj[this.config.label[0]()]);
        return 15;
    },
    hardCoded:true
    }*/
    if(!config){
        this.config = {
            label:{val:"machine"},
            y:{val:"model_throughput",label:"SYPD"},
            x:{val:"total_pes_active",label:"Total PEs"},
            r:{val:15,hardCoded:true}
        }
    }

    this.chart = new Chart(id,{
        type:"bubble",
        data: { datasets:[] },
        options: {
            scales: {
                yAxes:[{
                    scaleLabel:{
                        display:true,
                        labelString:this.config.y.label?this.config.y.label:
                        typeof(this.config.y.val) == "function"?this.config.y.val():
                        this.config.y.val
                    }}],
                xAxes:[{
                    scaleLabel:{
                        display:true,
                        labelString:this.config.x.label?this.config.x.label:
                        typeof(this.config.x.val) == "function"?this.config.x.val():
                        this.config.x.val
                    }}]
            }
        }
    });

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
            if(typeof(this.config[key].val) == "function" && this.config[key].dbFriendly)
                dbValueStr+=","+this.config[key].val();
            else if(!this.config[key].hardCoded)
                dbValueStr+=","+this.config[key].val;
        });
        $.get(detectRootUrl()+"ajax/specificSearch/"+query+"/"+dbValueStr,data=>{
            resultData = JSON.parse(data);
            let newColors = false;
            resultData.forEach(obj=>{
                //Initialize config variables:
                let configData = {};
                Object.keys(this.config).forEach(key=>{
                    if(typeof(this.config[key].val) == "function")
                        configData[key] = this.config[key].hardCoded?this.config[key].val(obj):obj[this.config[key].val(obj)];
                    else configData[key] = this.config[key].hardCoded?this.config[key].val:obj[this.config[key].val];
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