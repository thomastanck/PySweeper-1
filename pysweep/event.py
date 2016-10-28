class Event:
    def __init__(self):
        self.pysweep_node = None

class DictEvent(dict, Event):
    """
    A event object that acts like a dict. It's probably easiest to use this
    unless you want to subclass Event yourself for some special lulz.
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        Event.__init__(self)

class EventNode:
    """
    Supposed to be some parent class or something. "saa..."
    """
    def __init__(self, modname, name, parent, event):
        self.modname = modname
        self.name = name
        self.parent = parent
        self.children = []
        self.event = event

    def __str__(self):
        return ("{" + "modname:'{}',name:'{}',event:{},children:{}".format(
            self.modname,
            self.name,
            self.event,
            self.children
        ) + "}")

    def __repr__(self):
        return self.__str__()
