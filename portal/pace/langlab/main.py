from microapp import Project
from langlab.parsemk import ParseMakefile

class Langlab(Project):
    _name_ = "langlab"
    _version_ = "0.3.0"
    _description_ = "Microapp project for programming languages"
    _long_description_ = "Microapp project for programming languages"
    _author_ = "Youngsung Kim"
    _author_email_ = "youngsung.kim.act2@gmail.com"
    _url_ = "https://github.com/grnydawn/langlab"
    _builtin_apps_ = [ParseMakefile]

    def __init__(self):
        pass
