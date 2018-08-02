#! /usr/bin/bash
/opt/venv/pace/bin/gunicorn --bind 0.0.0.0:8001 \
		myapp:application \
		--error-logfile /pace/dev1/portal/gunicorn.log -D --log-level debug --capture-output 
