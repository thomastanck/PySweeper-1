from pysweep.mod import Mod, pysweep_listen, pysweep_trigger
from pysweep.event import DictEvent

class ListenerMod(Mod):
    @pysweep_listen("TriggerMod", "trigger")
    def listener(self, event):
        print("Zomg I've been triggered! Event: {}".format(event))
        self.managed_to_listen(event)

    @pysweep_trigger
    def managed_to_listen(self, event):
        e = DictEvent(event)
        e['event2'] = 'I got the message, bro.'
        return event, e
