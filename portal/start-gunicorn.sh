#! /usr/bin/bash
/opt/venv/pace/bin/gunicorn --bind 0.0.0.0:8002 \
		myapp:application \
		--error-logfile /pace/dev2/portal/gunicorn.log -D --log-level debug --capture-output
