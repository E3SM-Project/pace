#!/bin/bash
#This is a loop to keep pace containers running regardless of a crash. It will NOT restart flask.
#It also creates a .pacerc file if one doesn't exist.
# set -x
cd docker;
echo $(pwd)
dockerpath=/pace/docker
if [ ! -f docker/rc/.pacerc ];
    then if (($#)); then
        argStr=""
        while (($#)); do
            argStr="$argStr $1";
            shift
        done
        python "$dockerpath"/newRc.py $argStr >> "$dockerpath"/rc/.pacerc;
        else python "$dockerpath"/newRc.py $PACE_RC_DEFAULTS >> "$dockerpath"/rc/.pacerc;
    fi
    chmod 600 "$dockerpath"/rc/.pacerc
fi
if [ $PACE_DEV ];
    then 
    #service ssh start;
    export FLASK_ENV=development;
    fi
# set +x
python /pace/portal/dockerInit.py&
while [ 1 = 1 ]; do sleep 360;done