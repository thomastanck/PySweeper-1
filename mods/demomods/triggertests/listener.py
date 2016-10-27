from pysweep.mod import Mod, pysweep_listen, pysweep_trigger
from pysweep.event import Event

class ListenerMod(Mod):
    @pysweep_listen("TriggerMod", "trigger")
    def listener(self, event):
        print("Zomg I've been triggered! Event: {}".format(event))
        self.managed_to_listen(event)

    @pysweep_trigger
    def managed_to_listen(self, event):
        return event, Event('I got the message, bro.')

mods = {"ListenerMod": ListenerMod}
