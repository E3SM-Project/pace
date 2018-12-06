#!/usr/bin/env python
"""
Read timing files from ACME runs and make a plot showing 
the time spent in various aspects of the atmos model.
"""

import pylab as pl
import matplotlib as mpl
mpl.use("svg")
import numpy as np
#If converting this to python 3, use io.StringIO (if supported by python 3's matplotlib)
import StringIO
from modelTiming import searchNode
import types

#For maximum flexibility, this was moved to a dictionary:
timerNames = {
    "tot_time":'CPL:ATM_RUN', #total time
    "cam_run2_time":'a:CAM_run2', #tphysac+p_d_coupling
    "phys_run2_time":'a:phys_run2', #tphysac
    "stepon_run2_time":'a:stepon_run2', #p_d_coupling
    "cam_run3_time":'a:CAM_run3',
    "stepon_run3_time":'a:stepon_run3',#dyn
    "cam_run4_time":'a:CAM_run4', #atm hist
    "stepon_run1_time":'a:stepon_run1', #d_p_coupling
    "cam_run1_time":'a:CAM_run1', #d_p_coupling + tphysbc
    "phys_run1_time":'a:phys_run1', #tphysbc

    "convect_time":'a:moist_convection', #all convection
    "macro_time":'a:macrop_tend', #CLUBB
    "microp_aero_time":'a:microp_aero_run', #micro aerosol?
    "microp_time":'a:microp_tend', #microphys
    "bcaero_time":'a:bc_aerosols', #micro aerosol?
    "rad_time":'a:radiation', #radiation

    "hist_time":'a:wshist', #write out.
}

def render(threadList):
    chartWidth = 2*len(threadList)
    if len(threadList) <= 2:
        chartWidth = 5
    pl.figure(figsize=[chartWidth,5])
    #pl.subplots_adjust(left=0.18)

    #This is the width of one bar
    width = .8 / len(threadList)

    ind=-1
    #This value Contains all the data for the chart to display
    L=[]

    #"Legend String"
    #VERSION WHICH EXPANDS TPHYSBC
    legs=['Convect','CLUBB','Aerosol','Micro','Rad','Phys Aft Sfc','Dyn','Phys/Dyn Coupling','Hist','Other']
    cols=[tuple(np.array([0,0,153.])/255.),'b',tuple(np.array([102,178,255.])/255.),'g','y',tuple(np.array([255,153,51])/255.),'r',tuple(np.array([255,51,255])/255.),tuple(np.array([153,0,153])/255.),'k']
    
    for exp in threadList:
        ind+=1
        #Each key in here is based on timerNames. The variable is refreshed per-file.
        timerValues = {}
        for key in timerNames.keys():
            # print(searchNode(exp[1],timerNames[key]))
            targetTimerVals = searchNode(exp[1],timerNames[key])["values"]
            if "wallmax" in targetTimerVals.keys():
                timerValues[key] = targetTimerVals["wallmax"]
                #print(timerValues[key])


        #SANITY CHECKS THAT THE MAIN PARTS WE MEASURE SUM TO THE TOTAL TIME SPENT:
        #=========================================================================
        #print 'total atm time = %e, while sum of cam_run* = %e.'%(tot_time,cam_run1_time+cam_run2_time+cam_run3_time+cam_run4_time)
        #print 'phys_run1_time = %e, while sum of terms = %e.'%(phys_run1_time,convect_time+macro_time+microp_aero_time+microp_time+bcaero_time+rad_time)


        #MAKE BAR CHART SHOWING TIME SPENT IN VARIOUS PARTS OF CODE:
        #=========================================================================

        #MORE ABBREVIATED VERSION
        #legs=['Phys Bef Sfc','Phys Aft Sfc','Dyn','Phys/Dyn Coupling']
        #parts=np.array([0,phys_run1_time,phys_run2_time,stepon_run3_time,stepon_run2_time+stepon_run2_time])/tot_time
        #cols=['c','b','r','y']
        #width=0.4

        partsList = []
        #If an element in this for-loop is a string, it's considered and index to timerValues, otherwise, just add it to partsList:
        for element in [0,"convect_time","macro_time",(timerValues["microp_aero_time"]+timerValues["bcaero_time"]),"microp_time","rad_time","phys_run2_time","stepon_run3_time",(timerValues["stepon_run2_time"]*2),"hist_time"]:
            if type(element) == types.StringType:
                partsList.append(timerValues[element])
            else:
                partsList.append(element)

        parts=np.array(partsList)/timerValues["tot_time"]
        #print(parts)

        spacing = .5
        if len(threadList) > 2:
            spacing = .3

        for k in range(1,len(parts)): #start at 1 so parts[0]='start w/ zero stack' works.
            L.append(pl.bar([ spacing*ind ],parts[k],width,bottom=np.sum(parts[0:k]),color=cols[k-1]))
            #pl.text(0.5*ind,0.5*parts[k]+np.sum(parts[0:k]),legs[k-1],fontsize=12,fontweight='demi')

        #This appears to be on purpose, if all other processes don't add up to 1, this fills the rest of the chart up.
        L.append(pl.bar([spacing*ind ],1,width,bottom=np.sum(parts),color='k'))
        #/ len(threadList)
    pl.legend(L,legs)
    pl.ylabel('Frac Time in Routine')
    pl.axis([-0.2,1.7,0,1])

    #The labels will be the short names for the res
    labelPush = -.2
    for exp in threadList:
        pl.text(labelPush,pl.axis()[3]+0.03,exp[0],fontsize=16)
        if len(threadList) == 2:
            labelPush+=.5
        else:
            labelPush+=.3

    pl.xticks([])

    fileObj = StringIO.StringIO()
    pl.savefig(fileObj)
    fileObj.seek(0)
    return fileObj