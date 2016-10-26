from pysweep.mod import Mod, pysweep_listen

class ListenerMod(Mod):
    @pysweep_listen("TriggerMod", "trigger")
    def listener(self, event):
        print("Zomg I've been triggered! Event: {}".format(event))
        return 5

mods = {"ListenerMod": ListenerMod}
