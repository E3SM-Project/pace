#! /usr/bin/bash
/opt/venv/pace/bin/gunicorn --bind 0.0.0.0:8003 -w 4 -k gevent \
		myapp:application \
		--error-logfile /pace/dev3/portal/gunicorn.log -D --log-level debug --capture-output
