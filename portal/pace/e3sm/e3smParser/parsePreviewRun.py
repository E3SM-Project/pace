
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
        'mpirun': None
    }

    try:
        mpifound=False
        with gzip.open(previewfile, 'rt') as f:
            for line in f:
                if mpifound and not data['mpirun']:
                    data['mpirun']=line.strip()
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
        
        if all(value == None for value in data.values()):
            return None
        return data
    except:
        print("Error encountered while parsing build time file : %s" %previewfile)