export FLASK_ENV=development;
python ./portal/dockerInit.py&
while [ 1 = 1 ]; do sleep 360;done