"""
The core engine PySweeper runs on. This will load modules and set up the
most basic of interactions between them.
"""

import pysweep.modloader

class PySweep:
    def __init__(self, master):
        self.master = master

        self.mods = pysweep.modloader.load_mods_in("mods", "~/.pysweeper/mods")

        print(self.mods)
        for mod in self.mods.values():
            mod.pysweep_init(self)
