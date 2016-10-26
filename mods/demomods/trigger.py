from pysweep.mod import Mod, pysweep_trigger
from pysweep.event import Event

class TriggerMod(Mod):
    @pysweep_trigger
    def trigger(self):
        print("I'm gonna trigger you so hard, listener!")
        return Event()

mods = {"TriggerMod": TriggerMod}
