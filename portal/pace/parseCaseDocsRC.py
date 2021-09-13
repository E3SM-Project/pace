import sys, gzip

def loaddb_rcfile(rcpath):

    try:
        rcitems = []
        with gzip.open(rcpath, 'rt') as f_in:
            for line in f_in.read().strip().split("\n"):
                items = tuple(l.strip() for l in line.split(":"))

                if len(items)==2:
                    rcitems.append('"%s":%s' % items)
        f_in.close()
        
        jsondata = "{%s}" % ",".join(rcitems) 
        
        return jsondata

    except:
        print("Something went wrong with %s" %rcpath)

if __name__ == "__main__":
    rcpath = sys.argv[1]
    print(loaddb_rcfile(rcpath))