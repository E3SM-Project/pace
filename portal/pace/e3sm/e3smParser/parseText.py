import gzip

def load_text(file):
    data = None

    try:
        with gzip.open(file, 'rt') as f:
            data = f.read()
        if not data:
            return None
        return data

    except:
        print("Error encountered while parsing user_nl namelist file: %s" %file)
        return None