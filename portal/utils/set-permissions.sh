#! /bin/bash

# Note: This needs sudo permissions

mydate=$(date +'%F-%T')
export PACE_WEBAPP_DIR=/pace/prod
# cp -r $PACE_WEBAPP_DIR $PACE_WEBAPP_DIR.bak.$mydate

chown -R portal.webdevs $PACE_WEBAPP_DIR
chmod -R g+w  $PACE_WEBAPP_DIR
mkdir -p $PACE_WEBAPP_DIR/portal/upload
chmod 600 /pace/prod/.pacerc
