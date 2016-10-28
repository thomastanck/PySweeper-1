import pysweep.time as ptime

import pysweep.mod as mod
from pysweep.event import Event, EventNode

class TkinterEvent(Event):
    def __init__(self, eventtype, eventname, event):
        Event.__init__(self)
        self.eventtype = eventtype
        self.eventname = eventname
        self.event = event
        self.time = ptime.time()

    def __str__(self):
        return '{'+"eventtype:'{}',eventname:'{}',time:{}".format(self.eventtype, self.eventname, self.time)+'}'

    def __repr__(self):
        return str(self)

class TkinterListener(mod.Mod):
    def __init__(self):
        self.triggers = {}

    def pysweep_register(self, trigger, func):
        """
        Called by other mods to register a callback with a trigger.

        We overload it here because tkinter has many events and it'd be stupid
        to create a new function every time we needed one :)
        """
        if type(trigger) != tuple:
            trigger = ('event', trigger)
        eventtype, eventname = trigger
        if trigger not in self.triggers:
            self.pysweep.master.bind(eventname, lambda event,trigger=trigger: self.handle_event(trigger, event))
            self.triggers[trigger] = []
        self.triggers[trigger].append(func)

    def handle_event(self, trigger, event):
        event = TkinterEvent(trigger[0], trigger[1], event)
        eventnode = EventNode(type(self).__name__, trigger, None, event)
        event.pysweep_node = eventnode
        for listener in self.triggers[trigger]:
            listener(event)

    # @mod.listen('TkinterListener', '<F2>')
    # def wowlistener(self, event):
    #     print('wow', event)
