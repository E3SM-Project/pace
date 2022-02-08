"""Converting E3SM XML json string to Javascript string for Tabulator table data"""

import sys, json


def gen_xml_tabulator(xml, out):
    """Converting E3SM xml data to Tabulator format

    Parameters:
    xml(object): a JSON object
    out(list): a buffer for accumulating converted strings

    Returns:
    None
    """

    if isinstance(xml, dict):
        for key, value in xml.items():
            if isinstance(value, dict):
                name, attrs = extract_xmlattrs(value)
                if name:
                    out.append(u"{name: '%s', value: '%s', _children:[" % (name, attrs))
                else:
                    out.append(u"{name: '%s', value: '%s', _children:[" % (key, attrs))
                gen_xml_tabulator(value, out)
                out.append(u"]},")

            elif isinstance(value, list):
                out.append(u"{name: '%s', value: '', _children:[" % key)
                gen_xml_tabulator(value, out)
                out.append(u"]},")

            else:
                text = tostr(value)
                try:
                    out.append(u"{name: '%s', value: '%s'}," % (key, text))
                except Exception as err:
                    print(err)

    elif isinstance(xml, list):

        for idx, value in enumerate(xml):

            if isinstance(value, dict):
                name, attrs = extract_xmlattrs(value)
                if name:
                    out.append(u"{name: '%s', value: '%s', _children:[" % (name, attrs))
                else:
                    out.append(u"{name: '%d', value: '%s', _children:[" % (idx, attrs))
                gen_xml_tabulator(value, out)
                out.append(u"]},")

            elif isinstance(value, list):
                out.append(u"{name: '%d', value: '', _children:[" % idx)
                gen_xml_tabulator(value, out)
                out.append(u"]},")

            else:
                out.append(u"{name: '%d', value: '%s'}," % (
                    idx, tostr(value)))

    else:
        print("ELSE")


def extract_xmlattrs(value):
    """Extract group id in E3SM xml data

    Parameters:
    value(dict): Python dictionary in json data

    Returns:
    tuple : Python typle of two items. First item is a id string if exists.
            If not exists id is None. Second item is the rest of attributes.
    """

    id = None
    attrs = []

    for key in list(value.keys()):

        if key.startswith(u"@"):
            if key == u"@id":
                id = value[key]

            else:
                attrs.append(u"%s=%s" % (key[1:], tostr(value[key])))

            del value[key]

    if id:
        id = u"%s" % id

    return id, u", ".join(attrs)


def tostr(value, escape=True):
    """Javascript string formatter

    Parameters:
    value(object): various Python object
    escape(bool): If true, add escape character for single quotes

    Returns:
    str: Javascript formatted string
    """


    if isinstance(value, list):
        text = u", ".join([tostr(v, False) for v in value])

    elif type(value) == type(u""):
        text = u"'%s'" % value

    elif isinstance(value, str):
        text = u"'%s'" % value.decode(u"utf-8")

    elif isinstance(value, bool):
        if value:
            text = u".true."

        else:
            text = u".false."

    elif value is None:
        return u""

    else:
        try:
            x = float(value)
            text = u"%s" % str(value)

        except Exception as err:
            print("Error: %s" % str(err))
            sys.exit(-1)

    if escape:
        text = text.replace(u"'", u"\\'")

    return text


def xmljson2tabulator(xmljson):
    """Driver for Converting XML json to tabulator string

    Parameters:
    xmljson(str): E3SM XML string in JSON format

    Returns:
    str: Javascript string for Tabulator table
    """

    xml = json.loads(xmljson)

    out = [u"["]

    gen_xml_tabulator(xml, out)

    out.append(u"]")

    if sys.version_info >= (3,):
        return u"".join(out)

    else:
        return u"".join(out).encode("utf-8")


if __name__ == "__main__":

    outs = ["["]

    # conversion for multiple files
    for jfile in sys.argv[1:]:
        with open(jfile) as f:
            out = xmljson2tabulator(f.read())
            outs.append(out[1:-1])

    outs.append("]")

    print("".join(outs).replace("\n", " "))
