#This file was created because of weird scoping + circular-import problems when using __init__.py in a container.
from pace.__init__ import *
import os
if __name__ == "__main__":
    runDebug = False
    if os.getenv("PACE_DEV") == '1':
        runDebug = True
    app.run(host="0.0.0.0",debug=runDebug,port=80)