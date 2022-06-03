
import gzip

def load_replayshFile(replayshfile):
    data = None

    try:
        with gzip.open(replayshfile, 'rt') as f:
            data = f.read()
        if not data:
            return None
        return data
    except:
        print("Error encountered while parsing replay.sh file : %s" %replayshfile)
        return None