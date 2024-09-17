#!/usr/bin/env python3

import os
import re
import shutil
from pathlib import Path
import subprocess
from datetime import datetime
import logging,sys
logger = logging.getLogger(__name__)

def process_dir_recursive(directory):
    for entry in os.listdir(directory):
        full_path = os.path.join(directory, entry)
        if os.path.isdir(full_path):
            # User job directories are of the format 
            if re.findall('^\d+\.\d+\-\d+$', entry):
                # print(full_path)
                # print(os.path.dirname(full_path))
                jobid = re.split('\.', entry)[0]

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

                # Don't move files associated with the following job statuses
                match jobstatus:
                    case 'PENDING':
                         continue;
                    case 'RESIZING':
                         continue;
                    case 'RUNNING':
                         continue;
                    case 'REQUEUED':
                         continue;

                # get corresponding user dir
                parents = Path(full_path).parents
                casename = os.path.basename(parents[0])
                username = os.path.basename(parents[1])
                logging.debug('User: ' + username + ' Case: ' + casename + ' Job: ' + jobid )

                newdir = './performance_archive_' + mytimestamp + '/' + jobstatus + '/' + username + '/' + casename
                logging.debug('Move ' + full_path + ' to ' + newdir);
                os.makedirs(newdir, exist_ok = True)
                shutil.move(full_path, newdir)
            else:
                process_dir_recursive(full_path)
            
        else:
            # Not a directory
            # print(full_path)
            continue;



if __name__ == '__main__':
    mytime = datetime.now()
    mytimestamp = mytime.strftime('%Y_%m_%d_%H_%M_%S')
    logfilename = 'process-perf-archive-' + mytimestamp + '.log'
    logging.basicConfig(filename=logfilename, level=logging.DEBUG)
    process_dir_recursive('/global/cfs/cdirs/e3sm/performance_archive')
