#!/usr/bin/env python3

import os
import re
import shutil
from pathlib import Path
import pathlib
import subprocess
import datetime
import logging,sys
import argparse
logger = logging.getLogger(__name__)

# color class
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    DARKGREY = '\033[90m'
    LIGHTGREY = '\033[37m'


def parseArguments():
    parser = argparse.ArgumentParser(description="PACE performance archive processing tool.")
    # Argument parser for E3SM experiments
    parser.add_argument('--machine','-m', action='store', required= True, help="Machine where tool is being run")
    parser.add_argument('--perf-archive','-pa', action='store', dest='perf_archive', help="Root directory containing performance archive. Handles multiple performance archive directories under root", type = pathlib.Path)
    parser.add_argument('--timestamp','-ts', action='store', dest='timestamp', default = None, help="Specify custom timestamp to use", type = datetime.date.fromisoformat)
    args = parser.parse_args()
    return args

def getJobStatus(jobid, machine):
    if (machine == 'frontier' or machine == 'perlmutter'):
        # For machines using Slurm scheduler
        # -X doesn't show sub-jobs, -n : suppress header
        # -p: parseable output, -b: brief
        result = subprocess.run(['sacct', '-Xnbp', '-j', jobid], capture_output = True, text = True)
        slurmout = result.stdout
        if slurmout:
            fulljobstatus = slurmout.split('|')[1]
            # Sometimes status is 'CANCELLED by 92714' 
            jobstatus = fulljobstatus.split(' ')[0]
            logging.debug('Job: ' + jobid + ' Status: ' + jobstatus)
        else:
            jobstatus = 'UNKNOWN'
    else:
        jobstatus = 'UNDEFINED_MACHINE'

    # Don't move files associated with the following job statuses
    # So, set the following skip flag
    match jobstatus:
        case 'PENDING':
             skip=True;
        case 'RESIZING':
             skip=True;
        case 'RUNNING':
             skip=True;
        case 'REQUEUED':
             skip=True;
        case _:
             skip=False;

    return (jobstatus, skip)


def process_dir_recursive(directory, timestamp, machine):
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            # User job directories are of the format 
            if re.findall('^\d+\.\d+\-\d+$', entry):
                # print(full_path)
                # print(os.path.dirname(full_path))
                jobid = re.split('\.', entry)[0]

                (jobstatus,skip) = getJobStatus(jobid,machine)
               
                # Don't move files associated with the following job statuses
                if skip == True:
                     continue;

                # get corresponding user dir
                parents = Path(full_path).parents
                casename = os.path.basename(parents[0])
                username = os.path.basename(parents[1])
                logging.debug('User: ' + username + ' Case: ' + casename + ' Job: ' + jobid )

                newdir = './performance_archive_' + timestamp + '/' + jobstatus + '/' + username + '/' + casename
                logging.debug('Move ' + full_path + ' to ' + newdir);
                os.makedirs(newdir, exist_ok = True)
                shutil.move(full_path, newdir)
            else:
                process_dir_recursive(full_path)


if __name__ == '__main__':
    myargs = parseArguments()

    logger.debug("Machine: " + myargs.machine)

    if (myargs.timestamp == None):
        mytime = datetime.datetime.now()
        mytimestamp = mytime.strftime('%Y_%m_%d_%H_%M_%S')
    else:
        mytimestamp = str(myargs.timestamp)

    logfilename = 'process-perf-archive-' + mytimestamp + '.log'
    logging.basicConfig(filename=logfilename, level=logging.DEBUG)

    if (myargs.perf_archive != None):
        perf_archive_dir = myargs.perf_archive
    else:
        if (myargs.machine == 'frontier'):
            perf_archive_dir = '/lustre/orion/cli115/proj-shared/performance_archive'
        elif (myargs.machine == 'perlmutter'):
            perf_archive_dir = '/global/cfs/cdirs/e3sm/performance_archive'
        
    logger.debug("Perf archive dir: " + myargs.perf_archive)
    logger.debug("Timestamp: " + myargs.timestamp)

    exit(2)
    process_dir_recursive(perf_archive_dir, mytimestamp, myargs.machine)
    
    # process_dir_recursive('/lustre/orion/cli115/proj-shared/performance_archive')
    # process_dir_recursive('/global/cfs/cdirs/e3sm/performance_archive')

