def insertInputs(zipfile, stdout, stderr=None):
    """parse e3sm input data and upload to pace database

    Parameters:
    zipfile(str): file path to a zipped e3sm data
    
    dbcfg is hardcoded for now
    dbcfg(str): file path to a pace database configuration ascii data.
                Only one item should exist in a line in four lines in total::

                    username
                    password
                    hostname
                    databasename

    stdout(file object): output file object
    stderr(file object): error file object. Optional

    Returns:
    int: return code

    Notes:
    * As of this version, this function works only if e3smlab is installed
        in Python 3. To make sure that e3smlab is installed in Python 3,
        use following command to install::

        python3 -m pip install e3smlab

    * This function assumes that e3smexp table exists and the table already
        has the expid of this zipped data. It may require to commit any staged
        transaction before calling this function.
    """

    import subprocess
    cmd = ["/opt/venv/pace3/bin/e3smlab", "pacedb", zipfile, "--db-cfg", "/pace/prod/portal/pace/e3smlabdb.cfg", "--commit"]
    # print ("Calling " + str(cmd) )
    return subprocess.call(cmd, stdout=stdout, stderr=stderr)

