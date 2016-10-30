import pysweep.mod as mod
from pysweep.event import Event

from clicker import ButtonState, Button, Action, ButtonAction

class ClickMode:
    """
    poor man's enum for keeping track of chords.

    This is because actual enums either need an external pip package or
    Python 3.4+
    """
    class Released:
        """
        State when all mouse buttons are up.

        In this state, RD toggles flag.
        """
        pass
    class BeforeChord:
        """
        Activated when a LD/RD arrives while in Released.

        In this state, LU opens a single tile.

        In this state, if LMB is down, the tile under the cursor gets
        a depressed animation.
        """
        pass
    class Chord:
        """
        Activated when a LD/MD/RD arrives while in BeforeChord, or when a MD
        arrives while in Released.

        Re-activated when a LD/MD/RD arrives while in AfterChord.

        In this state, LU/MU/RU performs a chord (opens all neighbours if the
        clicked tile is fulfilled).

        In this state, the tile under the cursor and its neighbours all get
        a depressed animation.
        """
        pass
    class AfterChord:
        """
        Activated when LU/MU/RU arrives while in Chord AND at least
        one mouse button is depressed (because Released is activated if there
        were no more buttons depressed).

        In this state, no actions are performed, and there are no depressed
        animations.
        """
        pass

class ClickAction:
    """
    poor man's enum for board actions performed after a click event.

    This is because actual enums either need an external pip package or
    Python 3.4+
    """
    class Open:
        """
        Send out a TileOpen event if cursor is over a tile. (and not the panel, etc.)
        """
        pass
    class Flag:
        """
        Send out a Flag event if cursor is over a tile.
        """
        pass
    class Chord:
        """
        Send out a TileChord event if cursor is over a tile.
        """
        pass

# Some convenience functions
def is_button_down(buttonstate):
    return buttonstate > ButtonState.Released
def num_buttons_down(clickerevent):
    i = 0
    for n in range(3):
        if is_button_down(clickerevent.state[n]):
            i += 1
    return i

class ClickManager(mod.Mod):
    def __init__(self):
        self.depressed = set()
        self.clickmode = ClickMode.Released

    @mod.listen('Clicker', 'LD')
    @mod.listen('Clicker', 'LM')
    @mod.listen('Clicker', 'LU')
    @mod.listen('Clicker', 'MD')
    @mod.listen('Clicker', 'MM')
    @mod.listen('Clicker', 'MU')
    @mod.listen('Clicker', 'RD')
    @mod.listen('Clicker', 'RM')
    @mod.listen('Clicker', 'RU')
    def listen(self, clickerevent):
        clickaction = self.process_click(clickerevent)
        # print("{!s:>50} : {!s}".format(self.clickmode, clickaction))

    def process_click(self, clickerevent):
        if self.clickmode == ClickMode.Released:
            # Released
            if clickerevent.buttonaction == ButtonAction.LD:
                self.clickmode = ClickMode.BeforeChord
                return None
            elif clickerevent.buttonaction == ButtonAction.MD:
                self.clickmode = ClickMode.Chord
                return None
            elif clickerevent.buttonaction == ButtonAction.RD:
                self.clickmode = ClickMode.BeforeChord
                return ClickAction.Flag
            else:
                return None
        elif self.clickmode == ClickMode.BeforeChord:
            # BeforeChord
            if clickerevent.buttonaction == ButtonAction.LU:
                self.clickmode = ClickMode.Released
                return ClickAction.Open
            elif num_buttons_down(clickerevent) == 0:
                self.clickmode = ClickMode.Released
                return None
            elif num_buttons_down(clickerevent) >= 2:
                self.clickmode = ClickMode.Chord
                return None
            else:
                return None
        elif self.clickmode == ClickMode.Chord:
            # Chord
            if clickerevent.action == Action.U:
                if num_buttons_down(clickerevent) == 0:
                    self.clickmode = ClickMode.Released
                else:
                    self.clickmode = ClickMode.AfterChord
                return ClickAction.Chord
            else:
                return None
        elif self.clickmode == ClickMode.AfterChord:
            # AfterChord
            if clickerevent.action == Action.D:
                self.clickmode = ClickMode.Chord
                return None
            elif num_buttons_down(clickerevent) == 0:
                self.clickmode = ClickMode.Released
                return None
            else:
                return None
        else:
            raise RuntimeError('Invalid internal state: clickmode is not a ClickMode. Got: {}'.format(self.clickmode))
