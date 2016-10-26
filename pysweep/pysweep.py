"""
The core engine PySweeper runs on. This will load modules and set up the
most basic of interactions between them.
"""

import traceback

import pysweep.modloader

class PySweep:
    def __init__(self, master):
        self.master = master

        self.mods = pysweep.modloader.load_mods_in("mods", "~/.pysweeper/mods")

        print()
        print("Loading mods: {}".format(list(self.mods.keys())))
        print()
        mods_to_delete = []
        for modname, mod in self.mods.items():
            try: mod.pysweep_init(self)
            except Exception as e: traceback.print_exc(); mods_to_delete.append(modname);
        for modname in mods_to_delete: del self.mods[modname]
        mods_to_delete = []
        for modname, mod in self.mods.items():
            try: mod.pysweep_triggers_init()
            except Exception as e: traceback.print_exc(); mods_to_delete.append(modname);
        for modname in mods_to_delete: del self.mods[modname]
        mods_to_delete = []
        for modname, mod in self.mods.items():
            try: mod.pysweep_listeners_init()
            except Exception as e: traceback.print_exc(); mods_to_delete.append(modname);
        for modname in mods_to_delete: del self.mods[modname]
        mods_to_delete = []
        for modname, mod in self.mods.items():
            try: mod.pysweep_before_finish_init()
            except Exception as e: traceback.print_exc(); mods_to_delete.append(modname);
        for modname in mods_to_delete: del self.mods[modname]
        mods_to_delete = []
        for modname, mod in self.mods.items():
            try: mod.pysweep_finish_init()
            except Exception as e: traceback.print_exc(); mods_to_delete.append(modname);
        for modname in mods_to_delete: del self.mods[modname]

        print()
        print("Successfully loaded: {}".format(list(self.mods.keys())))
