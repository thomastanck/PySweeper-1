"""
Functions that load modules from directories
"""

import os, imp, inspect

import pysweep.mod

def load_mods_in(*paths):
    """
    Load all mods found in the directories pointed to by the paths list.

    Later elements override earlier elements.

    Returns a dict where keys are mod names and values are mods
    """
    module_path_dict = {}
    for path in paths:
        path = os.path.expanduser(path)
        if not os.path.isdir(path): # Just check if it exists and is a directory.
            print("Path {} not found or is not a directory, skipping.".format(path))
            continue
        module_path_dict.update(find_modules(path))

    print()

    name_module_dict = import_modules(module_path_dict)

    name_mod_dict = load_mods(name_module_dict)

    return name_mod_dict

def is_package_module(path):
    return os.path.isfile(os.path.join(path, '__init__.py'))

def is_file_module(path):
    return path.endswith('.py') and not os.path.basename(path).startswith('_')

def ignore_dir(path):
    return (os.path.basename(path).startswith("_") or os.path.basename(path).startswith("."))

def ignore_file(path):
    return os.path.basename(path).startswith(".")

def find_modules(path):
    """
    Finds modules in path.

    Returns a dict where the keys are the names of the modules (file/directory
    names) and the values are the paths to the modules.
    """
    return find_modules_r(path)[0]

def find_modules_r(path, alreadyfound=[]):
    """
    Finds modules in path recursively.

    Here we use alreadyfound to keep track of files/directories we've seen.
    The second value in the return tuple is the updated alreadyfound.
    """
    module_path_dict = {}

    for module_path in os.listdir(path):
        module_path = os.path.join(path, module_path)

        if os.path.isdir(module_path) and not ignore_dir(module_path):
            # DIRECTORY
            for found in alreadyfound:
                if os.path.samefile(module_path, found):
                    print("Already found: {}".format(module_path))
                    break
            else:
                # this module is not yet found
                print("Found: {}".format(module_path))
                alreadyfound.append(module_path)
                if is_package_module(module_path):
                    modulename = os.path.basename(module_path)
                    module_path_dict[modulename] = (module_path, imp.PKG_DIRECTORY)
                else:
                    # Was not a package module, recurse to find more modules inside
                    recurse = find_modules_r(module_path, alreadyfound)
                    module_path_dict.update(recurse[0])
                    alreadyfound = recurse[1]

        elif os.path.isfile(module_path) and not ignore_file(module_path):
            # FILE
            for found in alreadyfound:
                if os.path.samefile(module_path, found):
                    print("Already found: {}".format(module_path))
                    break
            else:
                # this module is not yet found
                print("Found: {}".format(module_path))
                alreadyfound.append(module_path)
                if is_file_module(module_path):
                    modulename = os.path.basename(module_path)[:-3]
                    module_path_dict[modulename] = (module_path, imp.PY_SOURCE)
    return (module_path_dict, alreadyfound)

def import_modules(module_path_dict):
    """
    Returns a dict where the keys are the module names and the values are the
    modules.
    """
    name_module_dict = {}
    for name in module_path_dict.keys():
        path, type_ = module_path_dict[name]
        name_module_dict[name] = (import_module(name, path, type_), path)
    return name_module_dict

def import_module(name, path, type_):
    """
    Returns the module pointed to by the path.
    """
    if type_ == imp.PY_SOURCE:
        with open(path) as module:
            module = imp.load_module(name, module, path, ('.py', 'U', type_))
    elif type_ == imp.PKG_DIRECTORY:
        module = imp.load_module(name, None, path, ('', '', type_))
    else:
        raise TypeError('Unsupported module type')
    return module

def load_mods(name_module_dict):
    """
    Returns a dict of mod names and the mod instances.

    Note the difference between mods and modules. Modules are the python
    modules that mods are in, and mods are the objects that interact with
    PySweeper and other mods.
    """

    name_mod_dict = {}

    for modulename, (module, path) in name_module_dict.items():
        print("Loading mods in module: {}".format(modulename))
        class_list = [m for m in
            inspect.getmembers(module, predicate=inspect.isclass)
            if m[1].__module__ == module.__name__]
        for modname, modclass in class_list:
            ismod, missing = pysweep.mod.ismod(modclass)
            if not ismod:
                print("Class '{}' in '{}' is not a mod as it is missing the following functions, skipping. (Found in: {}) Missing: {}".format(modname, modulename, path, missing))
                continue
            print("  Loading mod: {} ... ".format(modname), end="")
            mod = modclass()
            name_mod_dict[modname] = mod
            print("done")

    return name_mod_dict
