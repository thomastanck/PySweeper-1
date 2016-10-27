from pysweep.mod import Mod, pysweep_trigger
from pysweep.event import Event

class TriggerMod(Mod):
    def pysweep_finish_init(self):
        print()
        returnevent = self.pysweep.mods["TriggerMod"].trigger()
        print(returnevent)

    @pysweep_trigger
    def trigger(self):
        print("I'm gonna trigger you so hard, listener!")
        return None, Event('root cause')

mods = {"TriggerMod": TriggerMod}
