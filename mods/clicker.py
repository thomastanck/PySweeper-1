import platform

import pysweep.mod as mod
from pysweep.event import Event

class ButtonState:
    """
    poor man's enum for a button's state

    This is because actual enums either need an external pip package or
    Python 3.4+
    """
    Released =  0
    Releasing = 1
    Pressed =   2

class Button:
    class Any: n = -1
    class L:   n = 0
    class M:   n = 1
    class R:   n = 2

    @classmethod
    def i(cls, button_num):
        return (cls.L, cls.M, cls.R)[button_num]

class Action:
    class D: pass
    class M: pass
    class U: pass

class ButtonAction:
    class D: pass
    class M: pass
    class U: pass
    class LD: pass
    class LM: pass
    class LU: pass
    class MD: pass
    class MM: pass
    class MU: pass
    class RD: pass
    class RM: pass
    class RU: pass

    @classmethod
    def from_button_action(cls, button, action):
        if action == Action.D:
            return (cls.D, cls.LD, cls.MD, cls.RD)[button.n+1]
        elif action == Action.M:
            return (cls.M, cls.LM, cls.MM, cls.RM)[button.n+1]
        elif action == Action.U:
            return (cls.U, cls.LU, cls.MU, cls.RU)[button.n+1]
        else:
            raise ValueError('Invalid button/action combination ({}, {})'.format(button, action))

class InputType:
    class Keyboard: pass
    class Mouse: pass

class ClickerEvent(Event):
    def __init__(self, button, action, root_position, state):
        self.button = button
        self.action = action
        self.buttonaction = ButtonAction.from_button_action(self.button, self.action)
        self.root_position = root_position
        self.state = state

    def __str__(self):
        return '{'+"button:'{}',action:'{}',root_position:{},state:{}".format(self.button, self.action, self.root_position, self.state)+'}'

    def __repr__(self):
        return str(self)

class Clicker(mod.Mod):
    def __init__(self):
        # settings = [LMB key/mouse button, RMB key/mouse button]
        if platform.system() == 'Darwin':  # How Mac OS X is identified by Python
            self.keyboard_settings = ["3", "2", "1"]
            self.mouse_settings =    [1, 3, 2] # OSX uses mouse button 2 for right click. weird huh?
        else:
            self.keyboard_settings = ["3", "2", "1"]
            self.mouse_settings =    [1, 2, 3] # Everyone else uses mouse button 3 for right click.

        self.mouse_state = [ButtonState.Released] * 3
        self.key_state = [ButtonState.Released] * 3
        self.state = [ButtonState.Released] * 3
        self.root_position = (0, 0) # Relative to screen

    @mod.listen("TkinterListener", "<Motion>")
    def motion(self, event):
        self.root_position = (event.event.x_root, event.event.y_root)
        self.move(event)

    @mod.listen("TkinterListener", "<KeyPress>")
    def keydown(self, event):
        try:
            if event.event.char in self.keyboard_settings:
                self.down(event, Button.i(self.keyboard_settings.index(event.event.char)), InputType.Keyboard)
        except:
            raise
            print('wot')
            pass
    @mod.listen("TkinterListener", "<KeyRelease>")
    def keyup(self, event):
        try:
            if event.event.char in self.keyboard_settings:
                self.tryup(event, Button.i(self.keyboard_settings.index(event.event.char)), InputType.Keyboard)
        except:
            raise
            print('wot')
            pass
    @mod.listen("TkinterListener", "<ButtonPress-1>")
    def b1d(self, event): self.down(event, Button.i(self.mouse_settings.index(1)), InputType.Mouse)
    @mod.listen("TkinterListener", "<ButtonRelease-1>")
    def b1u(self, event): self.tryup(event, Button.i(self.mouse_settings.index(1)), InputType.Mouse)
    @mod.listen("TkinterListener", "<ButtonPress-2>")
    def b2d(self, event): self.down(event, Button.i(self.mouse_settings.index(2)), InputType.Mouse)
    @mod.listen("TkinterListener", "<ButtonRelease-2>")
    def b2u(self, event): self.tryup(event, Button.i(self.mouse_settings.index(2)), InputType.Mouse)
    @mod.listen("TkinterListener", "<ButtonPress-3>")
    def b3d(self, event): self.down(event, Button.i(self.mouse_settings.index(3)), InputType.Mouse)
    @mod.listen("TkinterListener", "<ButtonRelease-3>")
    def b3u(self, event): self.tryup(event, Button.i(self.mouse_settings.index(3)), InputType.Mouse)

    def down(self, event, button, inputtype):
        if inputtype == InputType.Mouse:
            self.mouse_state[button.n] = ButtonState.Pressed
        elif inputtype == InputType.Keyboard:
            self.key_state[button.n] = ButtonState.Pressed
        else:
            raise ValueError("{} is not an InputType.".format(inputtype))
        if self.state[button.n] == ButtonState.Released:
            self.state[button.n] = max(self.mouse_state[button.n], self.key_state[button.n])
            self.D(event)
            if button == Button.L: self.LD(event)
            if button == Button.M: self.MD(event)
            if button == Button.R: self.RD(event)
    def move(self, event):
        self.M(event)
        if self.state[0] > ButtonState.Released: self.LM(event)
        if self.state[1] > ButtonState.Released: self.MM(event)
        if self.state[2] > ButtonState.Released: self.RM(event)
    def tryup(self, event, button, inputtype):
        if inputtype == InputType.Mouse:
            self.mouse_state[button.n] = ButtonState.Released
        elif inputtype == InputType.Keyboard:
            self.key_state[button.n] = ButtonState.Releasing
            self.pysweep.master.after(0, lambda event=event,button=button: self.actuallykeyup(event, button))
        else:
            raise ValueError("{} is not an InputType.".format(inputtype))
        self.up(event, button)
    def actuallykeyup(self, event, button):
        if self.key_state[button.n] == ButtonState.Releasing:
            self.key_state[button.n] = ButtonState.Released
        self.up(event, button)
    def up(self, event, button):
        self.state[button.n] = max(self.mouse_state[button.n], self.key_state[button.n])
        if self.state[button.n] == ButtonState.Released:
            self.U(event)
            if button == Button.L: self.LU(event)
            if button == Button.M: self.MU(event)
            if button == Button.R: self.RU(event)

    @mod.trigger
    def D(self, event): return event, ClickerEvent(Button.Any, Action.D, self.root_position, self.state)
    @mod.trigger
    def M(self, event): return event, ClickerEvent(Button.Any, Action.M, self.root_position, self.state)
    @mod.trigger
    def U(self, event): return event, ClickerEvent(Button.Any, Action.U, self.root_position, self.state)

    @mod.trigger
    def LD(self, event): return event, ClickerEvent(Button.L, Action.D, self.root_position, self.state)
    @mod.trigger
    def LM(self, event): return event, ClickerEvent(Button.L, Action.M, self.root_position, self.state)
    @mod.trigger
    def LU(self, event): return event, ClickerEvent(Button.L, Action.U, self.root_position, self.state)

    @mod.trigger
    def MD(self, event): return event, ClickerEvent(Button.M, Action.D, self.root_position, self.state)
    @mod.trigger
    def MM(self, event): return event, ClickerEvent(Button.M, Action.M, self.root_position, self.state)
    @mod.trigger
    def MU(self, event): return event, ClickerEvent(Button.M, Action.U, self.root_position, self.state)

    @mod.trigger
    def RD(self, event): return event, ClickerEvent(Button.R, Action.D, self.root_position, self.state)
    @mod.trigger
    def RM(self, event): return event, ClickerEvent(Button.R, Action.M, self.root_position, self.state)
    @mod.trigger
    def RU(self, event): return event, ClickerEvent(Button.R, Action.U, self.root_position, self.state)

    # @mod.listen('Clicker', 'D')
    # @mod.listen('Clicker', 'M')
    # @mod.listen('Clicker', 'U')
    # @mod.listen('Clicker', 'LD')
    # @mod.listen('Clicker', 'LM')
    # @mod.listen('Clicker', 'LU')
    # @mod.listen('Clicker', 'MD')
    # @mod.listen('Clicker', 'MM')
    # @mod.listen('Clicker', 'MU')
    # @mod.listen('Clicker', 'RD')
    # @mod.listen('Clicker', 'RM')
    # @mod.listen('Clicker', 'RU')
    # def debug(self, event):
    #     print(event)
