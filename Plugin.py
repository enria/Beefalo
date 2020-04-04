class AbstractPlugin:
    keywords = {}
    _name_, _desc_, _icon_ = "abstract", "", ""

    def __init__(self, name, desc, icon):
        self._name_ = name
        self._desc_ = desc
        self._icon_ = icon
        self.callback = False

    def query(self, keyword, text):
        pass
