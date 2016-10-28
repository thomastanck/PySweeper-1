from pysweep.mod import Mod, pysweep_listen, pysweep_trigger
from pysweep.event import DictEvent

class ChainMod2(Mod):
    def __init__(self):
        self.counter = 0

    def pysweep_finish_init(self):
        print()
        print("Chained Trigger Demo 2")
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
        return None, DictEvent(event="A", counter=self.counter)

    @pysweep_listen("ChainMod2", "A")
    def B(self, event):
        print("B", self.counter)
        self.counter += 1
        self.C(event)

    def C(self, event):
        print("C", self.counter)
        self.counter += 1
        self.D(event)
        self.D(event)

    @pysweep_trigger
    def D(self, event):
        print("D", self.counter)
        self.counter += 1
        return event, DictEvent(event="D", counter=self.counter, parentcounter=event['counter'])
