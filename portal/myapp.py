import sys, os

import site
site.addsitedir('/var/www/portal')

from pace import app as application
application.debug = True

