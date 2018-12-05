#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 12 13:31:44 2017

@author: donahue5

Routine to create a block figure of the E3SM runtime results taken from the
case_scripts/timing/acme*** file produced by the model.

There are a handful of options that need to be set (see below):
    
For questions or comments contact: donahue5@llnl.gov
"""

#This is a modified version of donahue5's file. It's now geared toward being used more programatically. --Zachary Mitchell

###############################################################################
###                           Load Packages                                 ###
import numpy as np
import matplotlib as mpl
mpl.use("svg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.pyplot import cm 
import datetime
#If converting this to python 3, use io.StringIO (if supported by python 3's matplotlib)
import StringIO
###############################################################################
###                           Options                                       ###
##
default_args = {
    ## What datatype do you want to plot?
    #         "seconds" = total number of sec spent for each component (default)
    #         "model_day" = wall seconds per modeled day
    #         "model_years" = modeled years per wall day
    'dtype': "seconds",
    ## What components are you intersted in plotting?
    'comps': ['ICE','LND','ROF','WAV','OCN','ATM','GLC','CPL'],
    ## Do any of these components cause all PE's to stop and wait?
    'fullstop' : [False,False,False,False,False,False,False,True],
    'figname': "e3sm_timing_runtime",
    ## Do you want the pe-layout to be written on the side of the figure?
    'addlayout': False,
    }
## Do you have a block color preference?
# default_args['color'] = cm.rainbow(np.linspace(0,1,len(default_args['comps'])))
default_args['color'] = ["#00FFFF","#00ff40","#FF0000","#0000B0","#0000FF80","#66ccff","#FF99CC","#ff9900"]
###                       END Options                                       ###
###############################################################################
###############################################################################
###                       Begin Code                                        ###
# Class to describe basic info for each component
class pe_component(object):
    def __init__(self,nameIn,valuesIn):
        self.name = nameIn
        #self.pe_layout = None
        self.runtime = None
        self.color = None
        self.plot_patch = None
        self.fullstop = None
        self.values = valuesIn
        if "tasks" in self.values.keys() and "root_pe" in self.values.keys():
            self.root_task_sum = self.values["tasks"] + self.values["root_pe"]
            #print(self.name+": "+str([self.values["root_pe"],self.root_task_sum]))
    def __str__(self):
        print self.name
    
    def add2plot(self,ax,bdims,displayLabel):
        self.plot_patch = patches.Rectangle(bdims[0:2], bdims[2],bdims[3],color=self.color)
        self.plot_patch.set_clip_on(False)
        ax.add_artist(self.plot_patch)
        if bdims[3] > 0.0:
            rx, ry = self.plot_patch.get_xy()
            cx = rx + self.plot_patch.get_width()/2.0
            cy = ry + self.plot_patch.get_height()/2.0
            if displayLabel:
                ax.annotate(self.name, (cx, cy), color='k', weight='bold',fontsize=26, ha='center', va='center')
###############################################################################
def check_defaults(arg):
    # Pass a dictionary of all the arguments.  If any will cause an error then
    # change to default value.  Or kill run
    if not arg.get('dtype') in ("seconds","model_day","model_years"):
        print "ERROR: data type "+arg.get('dtype')+" not supported... "+\
                "changing to default data type = seconds"
        arg['dtype'] = "seconds"
    for ii in arg.get('comps'):
        if not ii in ('ICE','LND','ROF','WAV','OCN','ATM','GLC','CPL'):
            print """%s not a supported component please check my_comps variable
            Consider using default of:\n
            ['ICE','LND','ROF','WAV','OCN','ATM','GLC','CPL']"""
            return True
    if not len(arg.get('fullstop')) == len(arg.get('comps')):
        print "my_comps and full_stop are not equal in length.  Setting to " +\
                "default full_stop of all False"
        arg['fullstop'] = False*len(arg.get('comps'))
    if not len(arg.get('color')) == len(arg.get('comps')):
        print "Not all components have a designated color. Setting to default"
        arg['color'] = cm.rainbow(np.linspace(0,1,len(arg.get('comps'))))
    arg['color'] = iter(arg.get('color'))
    if not arg.get('figname'):
        arg[figname] = "timing_diagram_"+datetime.datetime.now().strftime("%Y%m%d.%H%M%S")
    if not arg.get('addlayout'):
        arg['addlayout'] = False
    return False
###############################################################################

#Render and export the graph to SVG:
def render(runtimeIn,opt_dict = None):
    #opt_dict wants to be a permanent variable even after the scope has run through once... Initializing below instead of arguments:
    if opt_dict == None:
        opt_dict = default_args.copy()
    errorflag = check_defaults(opt_dict)
    if errorflag:
        print "Error with options, cancelling run."
        quit()
    ## Load data and create plot
    comp_data = list()
    max_pe = 0
    TOT = pe_component("TOT",runtimeIn["TOT"])
    for ii in range(len(opt_dict['comps'])):
        cc = opt_dict.get('comps')[ii]
        node = pe_component(cc,runtimeIn[cc])
        node.color = next(opt_dict.get('color'))
        node.fullstop = opt_dict.get('fullstop')[ii]
        comp_data.append(node)
        max_pe = np.amax([max_pe,node.root_task_sum])
    if max_pe == 0:
        max_pe =1
    ## Build figure
    fig = plt.figure(figsize=[16,10])
    ax  = fig.add_subplot(111)
    ax.add_artist(patches.Rectangle((0,0),1.0,1.0,fill=False))
    ## Each component is built as a rectangle patch with
    ## width=pe_layout and height=runtime
    y_pts = [[-1,0,0]]
    xtcks = list()
    ytcks = list()
    layout = ''
    for cc in comp_data:
        bx = np.double(cc.values["root_pe"])/max_pe                       # box start X
        bw = np.double(cc.root_task_sum-cc.values["root_pe"])/max_pe       # box width
        bh = cc.values[opt_dict.get('dtype')]/TOT.values[opt_dict.get('dtype')]              # box height
        ## To determine box start y value think of Tetris
        by = 0.0                                      # box start Y

        for pt in y_pts:
            if cc.values["root_pe"] < pt[1] and cc.root_task_sum > pt[0]:
                by = np.amax([by,pt[2]])
        if not cc.fullstop:
            y_pts.append([cc.values["root_pe"],cc.root_task_sum,bh+by])
        else:
            y_pts.append([0,max_pe,bh+by])
        xtcks.append(cc.values["root_pe"])
        xtcks.append(cc.root_task_sum)
        ytcks.append(by+bh)

        #bdims[0:2], bdims[2],bdims[3]
        #patches.Rectangle([bx,by],bw,bh).get_height()

        #Display the label only if the result is greater than 1%
        displayLabel = True
        if cc.values["seconds"] < (TOT.values["seconds"] * 0.01):
            displayLabel = False
        cc.add2plot(ax,[bx,by,bw,bh],displayLabel)
        
        if max_pe>1e5:
            layout = "%s\n%s: (%6d,%6d)" %(layout,cc.name,cc.values["root_pe"],\
                              cc.root_task_sum)
        elif max_pe>1e4:
            layout = "%s\n%s: (%5d,%5d)" %(layout,cc.name,cc.values["root_pe"],\
                              cc.root_task_sum)
        #print(cc.name+": "+str(bh)+" | values: "+ str(cc.values[opt_dict.get('dtype')])+" / "+str(TOT.values[opt_dict.get('dtype')]))
    ## clean up xtcks
    xtcks_tmp = np.unique(xtcks)
    xtcks = list()
    xtcks.append(xtcks_tmp[0])
    for tt in xtcks_tmp[1:]:
        if np.double(tt - xtcks[-1])/max_pe > 0.03:
            xtcks.append(tt)
    ax.set_xticks(np.unique(np.double(xtcks)/max_pe))
    ax.set_yticks(np.append(np.unique(ytcks),1.0))
    ax.set_xticklabels(np.unique(xtcks),rotation=60,fontsize=16)
    ax.set_yticklabels(np.round(np.append(np.unique(ytcks)*TOT.values[opt_dict.get('dtype')],TOT.values[opt_dict.get('dtype')])),fontsize=16)
    ax.set_xlabel('Processor #',fontsize=20)
    ax.set_ylabel('Simulation Time (s)',fontsize=20)
    if opt_dict.get('addlayout'):
        ax.text(1.05,0.5,layout,fontsize=16)

    #Save to a file object:
    fileObj = StringIO.StringIO()
    plt.savefig(fileObj,dpi=400,bbox_inches='tight',facecolor="#00000000")
    fileObj.seek(0)
    return fileObj
###                               END Code                                  ###
###############################################################################
