if [ $PACE_DEV = 1 ];
    then service ssh start;
    export FLASK_ENV=development;
    fi
python ./portal/dockerInit.py&
while [ 1 = 1 ]; do sleep 360;done