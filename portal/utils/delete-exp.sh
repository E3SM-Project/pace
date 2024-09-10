#! /bin/bash
##
# @file delete-exp.sh
# @brief: Delete specified experiment from PACE
# @author Sarat Sreepathi
# @version 1.0
# @date 2019-07-25

USAGE="Usage: delete-exp.sh <expid>"

# Check arguments
if [ $# -eq 0 ] ; then
    echo $USAGE
    exit 1;
fi

myid=$1

OURDB_CMDS=$(cat <<EOF 
delete from model_timing where expid = $myid;
delete from exp where expid = $myid;
delete from pelayout where expid = $myid;
delete from runtime where expid = $myid;
delete from build_time where expid = $myid;
delete from expnotes where expid = $myid;
delete from makefile_inputs where expid = $myid;
delete from memfile_inputs where expid = $myid;
delete from namelist_inputs where expid = $myid;
delete from preview_run where expid = $myid;
delete from rc_inputs where expid = $myid;
delete from scorpio_stats where expid = $myid;
delete from script_files where expid = $myid;
delete from xml_inputs where expid = $myid;
delete from e3smexp where expid = $myid;
EOF
)


read -p "Delete experiment id: $myid. Are you sure? (y/n): " -n 1 -r
echo    # (optional) move to a new line
if [[ $REPLY =~ ^[Yy]$ ]]
then
    # experiment deletion
	echo "$OURDB_CMDS"
	echo "$OURDB_CMDS" | mysql -u sarat -p pace 

	# remember to delete associated files
	rm /pacefs/pace-exp-files/exp-*-${myid}.zip
	rm /pacefs/minio/e3sm/exp-*-${myid}.zip
fi
