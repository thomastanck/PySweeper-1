"""
Contains the parent class all mods should inherit from, and some utility
functions mods will need to use.
"""

import inspect
import functools

from pysweep.event import EventNode

def listen(mod, trigger):
    """
    Decorator for methods that need to be callable by other mods.
    """
    def decorate(f):
        try:
            f.pysweep_listening_to
        except:
            f.pysweep_listening_to = []
        f.pysweep_listening_to.append((mod, trigger))
        return f
    return decorate

def trigger(f):
    """
    Decorator for methods that need to trigger mods listening to this event.

    The method should return the event object it received and an event object
    which will be passed to the mods listening to this function.

    Any method that does something another mod might be interested in should
    use this decorator and then return an Event to indicate that a thing was
    done.
    """
    @functools.wraps(f)
    def _wrap(self, *args, **kwargs):
        rootevent, event = f(self, *args, **kwargs)
        if rootevent != None:
            rootnode = rootevent.pysweep_node
        else:
            rootnode = None
        eventnode = EventNode(type(self).__name__, f.__name__, rootnode, event)
        event.pysweep_node = eventnode
        if rootnode != None:
            rootnode.children.append(eventnode)
        for listener in self.triggers[f.__name__]:
            listener(event)
        return eventnode
    _wrap.pysweep_is_trigger = True
    return _wrap

def ismod(cl):
    """
    Determines if a class is a mod or not by checking it has all the right
    functions. I'm not sure if it'd be better to just test if it's a subclass
    of Mod, but duck typing! \o/
    """
    modset = {fname for fname, _ in inspect.getmembers(Mod, predicate=inspect.isfunction)}
    clset = {fname for fname, _ in inspect.getmembers(cl, predicate=inspect.isfunction)}
    missing = modset - clset
    return len(missing) == 0, missing

class Mod:
    """
    Parent class for all mods
    """
    def __init__(self):
        """
        Called 1st. No guarantees about any other mods.
        """
        pass

    def pysweep_init(self, pysweep):
        """
        Called 2nd.
        All mods have been __init__ but nothing else is done
        """
        self.pysweep = pysweep

    def pysweep_triggers_init(self):
        """
        Called 3rd.
        Set up triggers so other mods can listen to them
        """
        self.triggers = {}
        for funcname, func in inspect.getmembers(self, predicate=inspect.ismethod):
            try:
                func.pysweep_is_trigger
            except:
                continue
            if func.pysweep_is_trigger:
                self.triggers[func.__name__] = []

    def pysweep_listeners_init(self):
        """
        Called 4th.
        Listen to the other mods' triggers now that they've been set up.
        """
        for funcname, func in inspect.getmembers(self, predicate=inspect.ismethod):
            try:
                func.pysweep_listening_to
            except:
                continue

            for mod, trigger in func.pysweep_listening_to:
                self.pysweep.mods[mod].pysweep_register(trigger, func)

    def pysweep_before_finish_init(self):
        """
        Called 5th.
        Do something here if you want to trigger other mods!
        """
        pass

    def pysweep_finish_init(self):
        """
        Called 6th.
        This is the very last call. Be careful not to depend on the order
        mods are called!
        """
        pass

    def pysweep_register(self, trigger, func):
        """
        Called by other mods to register a callback with a trigger
        """
        if not hasattr(self, trigger):
            raise ValueError("Trigger {} does not exist".format(trigger))

        try:
            getattr(self, trigger).pysweep_is_trigger
        except Exception as e:
            raise ValueError("'{}' is not a trigger".format(trigger)) from e

        self.triggers[trigger].append(func)
