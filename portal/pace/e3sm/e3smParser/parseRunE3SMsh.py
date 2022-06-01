
from fileinput import filename
import gzip
import io

def load_rune3smshfile(rune3smshfile):
    data = None

    try:
        with gzip.open(rune3smshfile, 'rt') as f:
            data = f.read()
        if not data:
            return None
        return data
    except:
        print("Error encountered while parsing run_e3sm.sh file : %s" %rune3smshfile)
        return None