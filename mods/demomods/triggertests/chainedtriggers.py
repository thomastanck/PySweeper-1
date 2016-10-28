from pysweep.mod import Mod, pysweep_listen, pysweep_trigger
from pysweep.event import DictEvent

class ChainMod(Mod):
    """
    x - listens to -> y
    A <- B
    A <- C
    B <- C
    C <- D

    Note that in this example we have functions that both listen and trigger
    at the same time. However, it is probably a better idea to create separate
    trigger functions so you have more control over what you trigger.
    """
    def __init__(self):
        self.counter = 0

    def pysweep_finish_init(self):
        print()
        print("Chained Trigger Demo")
        print(self.triggers)
        print()
        e = self.A()
        print()
        print(e)
        print()

    @pysweep_trigger
    def A(self):
        print("A", self.counter)
        self.counter += 1
        return None, DictEvent(name="A", counter=self.counter)

    @pysweep_trigger
    @pysweep_listen("ChainMod", "A")
    def B(self, event):
        print("B", self.counter, event)
        self.counter += 1
        return event, DictEvent(name="B", counter=self.counter, parentcounter=event['counter'])

    @pysweep_trigger
    @pysweep_listen("ChainMod", "A")
    @pysweep_listen("ChainMod", "B")
    def C(self, event):
        print("C", self.counter, event)
        self.counter += 1
        return event, DictEvent(name="C", counter=self.counter, parentcounter=event['counter'])

    @pysweep_trigger
    @pysweep_listen("ChainMod", "C")
    def D(self, event):
        print("D", self.counter, event)
        self.counter += 1
        return event, DictEvent(name="D", counter=self.counter, parentcounter=event['counter'])

mods = {"ChainMod": ChainMod}
