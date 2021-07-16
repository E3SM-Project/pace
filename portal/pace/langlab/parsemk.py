import sys, os, pickle

from microapp import App
from langlab.pymake.parser import parsestring


class ParseMakefile(App):

    _name_ = "parsemk"
    _version_ = "0.1.0"

    def __init__(self, mgr):

        self.add_argument("makefile", type=str, help="makefile")
        self.add_argument("-s", "--split", action="store_true",
                          help="splitted makefile")

        self.register_forward("data", help="makefile object")

    def _to_source(self, obj):
        return obj.to_source()

#    def _picklable(self, obj):
#
#        if hasattr(obj, "vnameexp"):
#            obj.vnameexp.loc.path = None
#            #import pdb; pdb.set_trace()
#            #setattr(obj, "vnameexp", None)
#
#        if hasattr(obj, "valueloc"):
#            obj.valueloc.path = None
#        #    setattr(obj, "valueloc", None)

    def perform(self, args):

        mkfile = args.makefile["_"]

        if os.path.isfile(mkfile):
            filename = mkfile
            with open(mkfile) as f:
                mkfile = f.read()
        else:
            filename = "<string>"

        stmts = parsestring(mkfile, filename)

        if args.split:
            stmts = "\n".join(map(self._to_source, stmts))
            self.add_forward(data=stmts)
        else:
            self.add_forward(data=stmts)
