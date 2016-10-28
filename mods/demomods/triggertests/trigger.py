import pysweep.mod as mod
from pysweep.event import DictEvent

class TriggerMod(mod.Mod):
    def pysweep_finish_init(self):
        print()
        returnevent = self.pysweep.mods["TriggerMod"].trigger()
        print(returnevent)

    @mod.trigger
    def trigger(self):
        print("I'm gonna trigger you so hard, listener!")
        return None, DictEvent(event='root cause')
