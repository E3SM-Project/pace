"""Convert nested json string into Tabulator nested table data format"""

import sys, json


def nestedjson2tabulator(nestedjson):
    """Converting namelist json to tabulator string

    Parameters:
    nestedjson(str): E3SM namelist and other inputs in nested JSON format

    Returns:
    str: Tabulator nested data table format
    """

    inputjson = json.loads(nestedjson)

    out = ["["]

    for gname, group in inputjson.items():
        if group:
            out.append("{name: '%s', value: '', _children:[" % gname)
            for item, value in group.items():
                if isinstance(value, dict):
                    out.append("{name: '%s', value: '', _children:[" % item)
                    for k, v in value.items():
                        out.append("{name: '%s', value: '%s'}," % (
                                k, tostr(v)))
                    out.append("]},")
                else:
                    out.append("{name: '%s', value: '%s'}," % (
                                item, tostr(value)))
            out.append("]},")
        else:
            out.append("{name: '%s', value: ''}," % gname)

    out.append("]")

    return "".join(out)


def tostr(value, escape=True):
    """Javascript string formatter

    Parameters:
    value(object): various Python object
    escape(bool): If true, add escape character for single quotes

    Returns:
    str: Javascript formatted string
    """


    if isinstance(value, list):
        text = ", ".join([tostr(v, False) for v in value])

    elif isinstance(value, str):
        text = "'%s'" % value

    elif isinstance(value, bool):
        if value:
            text = ".true."

        else:
            text = ".false."
    else:
        try:
            x = float(value)
            text = str(value)

        except Exception as err:
            if type(value) == type(u""):
                text = "'%s'" % value.encode("utf-8")

            else:
                print("Error: %s" % str(err))
                sys.exit(-1)

    if escape:
        text = text.replace("'", "\\'")

    return text


if __name__ == "__main__":

    for jfile in sys.argv[1:]:
        with open(jfile) as f:
            print(nestedjson2tabulator(f.read()))
