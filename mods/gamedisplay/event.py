from pysweep.event import Event

class DisplayEvent(Event):
    def __init__(self, part, *args):
        Event.__init__(self)
        self.part = part
        self.args = args
