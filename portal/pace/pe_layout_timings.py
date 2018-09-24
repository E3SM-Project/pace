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
import sys
###############################################################################
###                           Options                                       ###
##
default_args = {
    ## What datatype do you want to plot?
    #         "runtime" = total number of sec spent for each component (default)
    #         "sec_per_day" = wall seconds per modeled day
    #         "myears_per_wday" = modeled years per wall day
    'dtype': "runtime",
    ## What components are you intersted in plotting?
    'comps': ['ICE','LND','ROF','WAV','OCN','ATM','GLC','CPL'],
    ## Do any of these components cause all PE's to stop and wait?
    'fullstop' : [False,False,False,False,False,False,False,True],
    'figname': "e3sm_timing_runtime",
    ## Do you want the pe-layout to be written on the side of the figure?
    'addlayout': True,
    ## What is the path to the timing file? 
    'timingfile': "e3smTiming.txt",
    }
## Do you have a block color preference?
default_args['color'] = cm.rainbow(np.linspace(0,1,len(default_args['comps'])))
###                       END Options                                       ###
###############################################################################
###############################################################################
###                       Begin Code                                        ###
# Class to describe basic info for each component
class pe_component(object):
    def __init__(self):
        self.name = None
        self.pe_layout = None
        self.runtime = None
        self.sec_per_day = None
        self.myears_per_wday = None
        self.color = None
        self.plot_patch = None
        self.fullstop = None
    
    def __str__(self):
        print self.name
    
    def load_data(self,name,datafile):
        self.name = name
        with open(datafile,'r') as f:
            tmp = f.readlines()
            for line in tmp:
                if line.count(" "+name+" Run Time") == 1:
                    mydata = line.split()
                    self.runtime = float(mydata[3])
                    self.sec_per_day = float(mydata[5])
                    self.myears_per_wday = float(mydata[7])
                if line.count(name+" (pes ") == 1:
                    mydata = line.split()
                    self.pe_layout = [int(mydata[2]),int(mydata[4][:-1])]
    def getdata(self,dtype):
        if dtype == "runtime":
            return self.runtime
        elif dtype == "sec_per_day":
            return self.sec_per_day
        elif dtype == "myears_per_wday":
            return self.myears_per_wday
    
    def add2plot(self,ax,bdims):
        self.plot_patch = patches.Rectangle(bdims[0:2], \
                                            bdims[2],bdims[3],color=self.color)
        self.plot_patch.set_clip_on(False)
        ax.add_artist(self.plot_patch)
        if bdims[3] > 0.0:
            rx, ry = self.plot_patch.get_xy()
            cx = rx + self.plot_patch.get_width()/2.0
            cy = ry + self.plot_patch.get_height()/2.0
            ax.annotate(self.name, (cx, cy), color='k', weight='bold', 
                    fontsize=26, ha='center', va='center')
###############################################################################
def check_defaults(arg):
    # Pass a dictionary of all the arguments.  If any will cause an error then
    # change to default value.  Or kill run
    if not arg.get('dtype') in ("runtime","sec_per_day","myears_per_wday"):
        print "ERROR: data type "+arg.get('dtype')+" not supported... "+\
                "changing to default data type = runtime"
        arg['dtype'] = "runtime"
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
def render(opt_dict = None):
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
    TOT = pe_component()
    TOT.load_data("TOT",opt_dict.get('timingfile'))
    for ii in range(len(opt_dict.get('comps'))):
        cc = opt_dict.get('comps')[ii]
        node = pe_component()
        node.load_data(cc,opt_dict.get('timingfile'))
        node.color = next(opt_dict.get('color'))
        node.fullstop = opt_dict.get('fullstop')[ii]
        comp_data.append(node)
        max_pe = np.amax([max_pe,node.pe_layout[1]])
    ## Build figure
    fig = plt.figure(figsize=[16,10])
    ax  = fig.add_subplot(111)
    ax.add_artist(patches.Rectangle((0,0),1.0,1.0,fill=False,hatch='//'))
    ## Each component is built as a rectangle patch with
    ## width=pe_layout and height=runtime
    y_pts = [[-1,0,0]]
    xtcks = list()
    ytcks = list()
    layout = ''
    for cc in comp_data:
        bx = np.double(cc.pe_layout[0])/max_pe                       # box start X
        bw = np.double(cc.pe_layout[1]-cc.pe_layout[0])/max_pe       # box width
        bh = cc.getdata(opt_dict.get('dtype'))/TOT.getdata(opt_dict.get('dtype'))              # box height
        ## To determine box start y value think of Tetris
        by = 0.0                                                     # box start Y
        for pt in y_pts:
            if cc.pe_layout[0] < pt[1] and cc.pe_layout[1] > pt[0]:
                by = np.amax([by,pt[2]])
        if not cc.fullstop:
            y_pts.append([cc.pe_layout[0],cc.pe_layout[1],bh+by])
        else:
            y_pts.append([0,max_pe,bh+by])
        xtcks.append(cc.pe_layout[0])
        xtcks.append(cc.pe_layout[1])
        ytcks.append(by+bh)
        cc.add2plot(ax,[bx,by,bw,bh])
        if max_pe>1e5:
            layout = "%s\n%s: (%6d,%6d)" %(layout,cc.name,cc.pe_layout[0],\
                              cc.pe_layout[1])
        elif max_pe>1e4:
            layout = "%s\n%s: (%5d,%5d)" %(layout,cc.name,cc.pe_layout[0],\
                              cc.pe_layout[1])
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
    ax.set_yticklabels(np.round(np.append(np.unique(ytcks)*TOT.getdata(opt_dict.get('dtype')),TOT.getdata(opt_dict.get('dtype')))),fontsize=16)
    ax.set_xlabel('Processor #',fontsize=20)
    ax.set_ylabel('Simulation Time (s)',fontsize=20)
    if opt_dict.get('addlayout'):
        ax.text(1.05,0.5,layout,fontsize=16)

    #Save to a file object:
    fileObj = StringIO.StringIO()
    plt.savefig(fileObj,dpi=400,bbox_inches='tight')
    fileObj.seek(0)
    plt.show()
    plt.close()
    return fileObj
###                               END Code                                  ###
###############################################################################