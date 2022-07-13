
#! /usr/bin/env python3
# @file parsePreviewRun.py
# @brief parser for preview_run.log.
# @author Gaurab KC
# @version 1.0
# @date 2022-05-13


import gzip
'''
    This functions parse preview_run.log file and retrives the CASE INFO and MPIRUN script
'''
def load_previewRunFile(previewfile):
    data = {
        'nodes': None,
        'total_tasks': None,
        'tasks_per_node': None,
        'thread_count': None,
        'ngpus_per_node': None,
        'env': None,
        'submit_cmd':None,
        'mpirun': None,
        'omp_threads': None
    }

    try:
        mpifound = False
        envfound = False
        cmdfound = False
        envdata = {}
        with gzip.open(previewfile, 'rt') as f:
            for line in f:
                if mpifound and not data['mpirun']:
                    data['mpirun']=line.strip()
                    mpifound = False
                if envfound and not data['env']:
                    words = line.split()
                    if 'Setting' in words:
                        envdataLine = words[-1].split('=')
                        if len(envdataLine) == 2:
                            envdata[envdataLine[0]] = envdataLine[1]
                        continue
                    else:
                        data['env']=envdata.copy()
                        if 'OMP_NUM_THREADS' in envdata:
                            data['omp_threads'] = envdata['OMP_NUM_THREADS']
                        envfound = False
                if cmdfound and not data['submit_cmd']:
                    data['submit_cmd']=line.strip()
                    cmdfound = False
                value = line.split()
                if 'nodes:' in value:
                    data['nodes'] = int(value[1])
                elif 'total' in value:
                    data['total_tasks'] = int(value[2])
                elif 'tasks' in value:
                    data['tasks_per_node'] = int(value[3])
                elif 'thread' in value:
                    data['thread_count'] = int(value[2])
                elif 'ngpus' in value:
                    data['ngpus_per_node'] = int(value[3])
                elif 'MPIRUN' in value:
                    mpifound = True
                elif 'ENV:' in value:
                    envfound = True
                elif 'SUBMIT' in value:
                    cmdfound = True
        
        if all(value == None for value in data.values()):
            return None
        return data
    except:
        print("Error encountered while parsing preview run file : %s" %previewfile)
