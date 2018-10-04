from pace.__init__ import *
import os.getenv
if __name__ == "__main__":
    runDebug = False
    if os.getenv("PACE_DEV") == '1':
        runDebug = True
    app.run(host="0.0.0.0",debug=runDebug,port=80)