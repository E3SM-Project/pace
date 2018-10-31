#Reset flask within your docker instance. Not ideal for production, but it can help with development of pace.
pkill -HUP python
python /pace/portal/dockerInit.py