# Purpose: Automate performance data upload to PACE
# Author: Sarat Sreepathi (sarat@ornl.gov)

# Allow group write permission for any files generated
umask 002 

echo "Begin PACE archiving."

MACHINE='frontier'
PERF_ARCHIVE_DIR='/lustre/orion/cli115/proj-shared/performance_archive'
OLD_PERF_ARCHIVE_DIR='/lustre/orion/cli115/proj-shared/OLD_PERF'
MYPYTHON='/sw/frontier/python/3.10/miniforge3/23.11.0/bin/python'

# source /usr/share/lmod/lmod/init/sh
# module load python

cd ${PERF_ARCHIVE_DIR}
# Performance archive should not contain large files (empirical threshold of 50MB)
# List any large files 
echo "Large file list:"
find . -size +50M -exec ls -lh {} \; > large-files-removed.txt
# Delete large files
find . -size +50M -exec rm {} \;

curdate=$(date '+%Y_%m_%d_%H_%M_%S')
${MYPYTHON} ${PERF_ARCHIVE_DIR}/pace-process-perf-archive.py --machine ${MACHINE} --timestamp ${curdate}
mkdir -p performance_archive_${curdate}
mv process-perf-archive-${curdate}.log performance_archive_${curdate}
${MYPYTHON} ${PERF_ARCHIVE_DIR}/pace-upload3 --perf-archive ./performance_archive_${curdate}

# Find handles the case gracefully when no pace*log is generated when no completed experiments were found
find . -iname "pace-*.log" -type f -exec mv {} performance_archive_${curdate} \;
mv large-files-removed.txt performance_archive_${curdate}


# Move processed exps into old perf data archive
curmonth=$(date '+%Y-%m')
mkdir -p ${OLD_PERF_ARCHIVE_DIR}/${curmonth}
mv performance_archive_${curdate}* ${OLD_PERF_ARCHIVE_DIR}/${curmonth}

# Clean up empty dirs
find . -type d -empty -delete

echo "Completed PACE archiving."
