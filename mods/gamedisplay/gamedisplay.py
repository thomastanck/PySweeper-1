from PIL import Image, ImageTk
import tkinter

from gamedisplay.displayimages import DisplayImages
from gamedisplay.event import DisplayEvent
from gamedisplay.state import TileState, FaceState

import pysweep.mod as mod

class GameDisplay(mod.Mod):
    def __init__(self):
        # Expose the state enums for other mods to see and use
        self.TileState = TileState
        self.FaceState = FaceState

        self.boardsize = (30, 16)

        self.images = DisplayImages('images')

        self.face = FaceState.Happy
        self.board = [[TileState.Unopened for i in range(self.boardsize[0])] for i in range(self.boardsize[1])]

    def pysweep_before_finish_init(self):
        """
        Create the display.
        """
        self.displaycanvas = DisplayCanvas(self.pysweep.master, self.boardsize, self.images)

    def pysweep_finish_init(self):
        """
        Create and show the display on the screen.
        """
        self.displaycanvas.pack()

class DisplayCanvas(tkinter.Canvas):
    def __init__(self, master, boardsize, images):
        self.boardsize = boardsize
        self.size = images.getsize(boardsize)

        super().__init__(master, width=self.size[0], height=self.size[1], highlightthickness=0)
        self.img = Image.new(size=self.size, mode="RGB", color='green')
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.img.paste(images.panel.face.happy, box=(10,10))
        self.tkimg.paste(self.img)
        self.create_image(0, 0, image=self.tkimg, anchor='nw')
