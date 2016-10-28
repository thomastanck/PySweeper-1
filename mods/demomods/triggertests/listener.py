import pysweep.mod as mod
from pysweep.event import DictEvent

class ListenerMod(mod.Mod):
    @mod.listen("TriggerMod", "trigger")
    def listener(self, event):
        print("Zomg I've been triggered! Event: {}".format(event))
        self.managed_to_listen(event)

    @mod.trigger
    def managed_to_listen(self, event):
        e = DictEvent(event)
        e['event2'] = 'I got the message, bro.'
        return event, e
