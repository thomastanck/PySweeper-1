from pysweep.event import Event

class DisplayEvent(Event):
    def __init__(self, part, *args):
        Event.__init__(self)
        self.part = part
        self.args = args

    def __str__(self):
        return '{'+"part:'{}',args:{}".format(self.part, self.args)+'}'

    def __repr__(self):
        return str(self)
