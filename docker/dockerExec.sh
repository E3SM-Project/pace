#!/bin/bash
#This is a loop to keep pace containers running regardless of a crash. It will NOT restart flask.
#It also creates a .pacerc file if one doesn't exist.
# set -x
if [ ! -f docker/rc/.pacerc ];
    then if (($#)); then
        if [ $1 = "-file" ]; then 
            echo -e "$2" >> /pace/docker/rc/.pacerc;
        else
            argStr=""
            while (($#)); do
                argStr="$argStr $1";
                shift
            done
            python docker/newRc.py $argStr >> docker/rc/.pacerc;
        fi
        else python docker/newRc.py $PACE_RC_DEFAULTS >> docker/rc/.pacerc;
    fi
    chmod 600 docker/rc/.pacerc
fi
if [ $PACE_DEV ];
    then 
    #service ssh start;
    export FLASK_ENV=development;
    fi
# set +x
python portal/dockerInit.py&
while [ 1 = 1 ]; do sleep 360;done