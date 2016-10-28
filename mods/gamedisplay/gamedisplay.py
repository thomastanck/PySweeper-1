import math

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

    def pysweep_before_finish_init(self):
        """
        Create the display.
        """
        self.displaycanvas = DisplayCanvas(self.pysweep.master, self.boardsize, 3, 3, self.images)

    def pysweep_finish_init(self):
        """
        Create and show the display on the screen.
        """
        self.displaycanvas.pack()

class DisplayCanvas(tkinter.Canvas):
    def __init__(self, master, boardsize, lcounterlength, rcounterlength, images):
        self.master = master
        self.boardsize = boardsize
        self.lcounterlength = lcounterlength
        self.rcounterlength = rcounterlength
        self.images = images
        self.size = self.images.getsize(boardsize, lcounterlength, rcounterlength)

        super().__init__(master, width=self.size[0], height=self.size[1], highlightthickness=0)

        self.update_queued = False

        self.img = Image.new(size=self.size, mode="RGB", color='green')
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.create_image(0, 0, image=self.tkimg, anchor='nw')

        maininsize = self.images.getinsize(boardsize, lcounterlength, rcounterlength)
        self.border = Border(self, (0, 0), self.images.getsize(boardsize, lcounterlength, rcounterlength), self.images.border)

        panelpos = (
            self.images.border.thickness[1],
            self.images.border.thickness[0],
        )
        panelsize = (
            maininsize[0],
            self.images.panel.getsize(lcounterlength, rcounterlength)[1],
        )
        self.panel = Panel(self, panelpos, panelsize, self.images.panel, lcounterlength, rcounterlength)

        boardpos = (
            self.images.border.thickness[1],
            self.images.border.thickness[0] + panelsize[1],
        )
        boardpixelsize = (
            maininsize[0],
            self.images.board.getsize(boardsize)[1],
        )
        self.board = Board(self, boardpos, self.images.board, boardpixelsize, self.boardsize)

        self.draw()
        # self.img.paste(Image.new(size=self.size, mode="RGB", color='blue'))
        # self.draw()

    def set_lcounter_value(self, value):
        return self.panel.set_lcounter_value(value)
    def set_face(self, face):
        return self.panel.set_face(face)
    def set_rcounter_value(self, value):
        return self.panel.set_rcounter_value(value)
    def set_tile(self, index, tile):
        return self.board.set_tile(index, tile)

    def paste(self, *args, **kwargs):
        self.img.paste(*args, **kwargs)
        self.update()

    def draw(self, force=False):
        """
        Parts should call draw on its child parts. It should determine if
        a change has been made, and if so, make the change and call update.

        If a part has pasted outside its region, it should return True

        Parts should not make changes to the display until draw has been called!
        This is because the order parts are drawn is important now that all
        parts share a single canvas. For example, the border should not
        be drawn before the panel's background is drawn, or else the panel's
        background may bleed over the panel into the borders.

        force can be set to True in order to force all parts to redraw.
        """
        self.panel.draw(force)
        self.board.draw(force)
        self.border.draw(force)

    def update(self):
        if not self.update_queued:
            self.update_queued = True
            self.master.after(0, self.actually_update)

    def actually_update(self):
        self.update_queued = False
        self.tkimg.paste(self.img)

class GridTile:
    """
    Repeatedly pastes an image a number of times in two directions.

    paste_amounts is a 2-tuple containing the number of times to paste in the x
    and y directions respectively.
    """
    def __init__(self, displaycanvas, position, paste_amounts, img):
        self.displaycanvas = displaycanvas
        self.position = position
        self.paste_amounts = paste_amounts
        self.imgsize = img.size
        self.img = img
        if self.imgsize == (1,1):
            self.pixel = img.getpixel((0,0))
        else:
            self.pixel = None
            if self.imgsize[0] == 1:
                self.resize = 'h'
            elif self.imgsize[1] == 1:
                self.resize = 'v'
            else:
                self.resize = None

        self.shoulddraw = True

    def draw(self, force):
        if not (force or self.shoulddraw):
            return
        self.shoulddraw = False
        if self.pixel is None:
            if self.resize == 'h':
                for row in range(self.paste_amounts[1]):
                    newsize = (self.paste_amounts[0], self.imgsize[1])
                    pastepos = (
                        self.position[0],
                        self.position[1] + self.imgsize[1] * row,
                    )
                    self.displaycanvas.paste(self.img.resize(newsize), pastepos)
            elif self.resize == 'v':
                for col in range(self.paste_amounts[0]):
                    newsize = (self.imgsize[0], self.paste_amounts[1])
                    pastepos = (
                        self.position[0] + self.imgsize[0] * col,
                        self.position[1],
                    )
                    self.displaycanvas.paste(self.img.resize(newsize), pastepos)
            else:
                for col in range(self.paste_amounts[0]):
                    for row in range(self.paste_amounts[1]):
                        pastepos = (
                            self.position[0] + self.imgsize[0] * col,
                            self.position[1] + self.imgsize[1] * row,
                        )
                        self.displaycanvas.paste(self.img, pastepos)
        else:
            pastearea = (
                self.position[0],
                self.position[1],
                self.position[0] + self.paste_amounts[0],
                self.position[1] + self.paste_amounts[1],
            )
            self.displaycanvas.paste(self.pixel, pastearea)

class Border:
    """
    Draws a box border using the 8 images provided.
    """
    def __init__(self, displaycanvas, position, size, borderimages):
        self.displaycanvas = displaycanvas
        self.position = position
        self.size = size
        self.borderimages = borderimages

        self.shoulddraw = True

    def draw(self, force):
        if not (force or self.shoulddraw):
            return
        self.shoulddraw = False
        self.insize = (
            self.size[0] - self.borderimages.size[0],
            self.size[1] - self.borderimages.size[1],
        )

        th, lw, _, _ = self.borderimages.thickness

        # Edges
        guide = {
            't': [(self.position[0] + lw + 0,              self.position[1] + 0),                   (self.insize[0], 1)],
            'b': [(self.position[0] + lw + 0,              self.position[1] + th + self.insize[1]), (self.insize[0], 1)],
            'l': [(self.position[0] + 0,                   self.position[1] + th + 0),              (1, self.insize[1])],
            'r': [(self.position[0] + lw + self.insize[0], self.position[1] + th + 0),              (1, self.insize[1])],
        }
        for k, v in guide.items():
            GridTile(self.displaycanvas, v[0], v[1], self.borderimages.i[k]).draw(force)

        # Corners
        guide = {
            'tl': (self.position[0] + 0,                   self.position[1] + 0),
            'tr': (self.position[0] + lw + self.insize[0], self.position[1] + 0),
            'bl': (self.position[0] + 0,                   self.position[1] + th + self.insize[1]),
            'br': (self.position[0] + lw + self.insize[0], self.position[1] + th + self.insize[1]),
        }
        for k, v in guide.items():
            self.displaycanvas.paste(self.borderimages.i[k], v)

class Panel:
    def __init__(self, displaycanvas, position, size, panelimages, lcounterlength, rcounterlength):
        self.displaycanvas = displaycanvas
        self.position = position
        self.size = size
        self.panelimages = panelimages

        self.insize = (
            self.size[0] - self.panelimages.border.size[0],
            self.size[1] - self.panelimages.border.size[1],
        )

        self.bganchor = (
            self.position[0] + self.size[0] // 2,
            self.position[1] + self.panelimages.border.thickness[0],
        )
        self.bgamount = (
            math.ceil(self.insize[0] / self.panelimages.bg.size[0]),
            math.ceil(self.insize[1] / self.panelimages.bg.size[1]),
        )
        self.bgpos = (
            self.bganchor[0] - self.bgamount[0] * self.panelimages.bg.size[0] // 2,
            self.bganchor[1],
        )
        self.bg = GridTile(self.displaycanvas, self.bgpos, self.bgamount, self.panelimages.bg)

        self.border = Border(self.displaycanvas, self.position, self.size, self.panelimages.border)

        self.lcounterpos = (
            self.position[0] + self.panelimages.border.thickness[1],
            self.position[1] + self.panelimages.border.thickness[0],
        )
        self.lcounter = Counter(self.displaycanvas, self.lcounterpos, self.panelimages.lcounter, lcounterlength)

        self.facepos = (
            self.position[0] + (self.size[0] - self.panelimages.face.size[0]) // 2,
            self.position[1] + self.panelimages.border.thickness[0],
        )
        self.face = Face(self.displaycanvas, self.facepos, self.panelimages.face)

        self.rcounterpos = (
            self.position[0] + self.size[0] - self.panelimages.border.thickness[2] - self.panelimages.rcounter.getsize(rcounterlength)[0],
            self.position[1] + self.panelimages.border.thickness[0],
        )
        self.rcounter = Counter(self.displaycanvas, self.rcounterpos, self.panelimages.rcounter, rcounterlength)

    def set_lcounter_value(self, value):
        return self.lcounter.set_value(value)
    def set_face(self, face):
        return self.face.set_face(face)
    def set_rcounter_value(self, value):
        return self.rcounter.set_value(value)

    def draw(self, force):
        self.bg.draw(force)
        self.border.draw(force)
        self.lcounter.draw(force)
        self.face.draw(force)
        self.rcounter.draw(force)

class Counter:
    def __init__(self, displaycanvas, position, counterimages, counterlength):
        self.displaycanvas = displaycanvas
        self.position = position
        self.counterimages = counterimages
        self.counterlength = counterlength

        self.size = (
            self.counterimages.border.size[0] + self.counterimages.digit.size[0] * counterlength,
            self.counterimages.border.size[1] + self.counterimages.digit.size[1],
        )

        self.border = Border(self.displaycanvas, self.position, self.size, self.counterimages.border)
        self.digitpos = []
        self.digits = []
        for i in range(counterlength):
            digitpos = (
                self.position[0] + self.counterimages.border.thickness[1] + self.counterimages.digit.size[0] * i,
                self.position[1] + self.counterimages.border.thickness[0],
            )
            self.digitpos.append(digitpos)
            self.digits.append(Digit(self.displaycanvas, digitpos, self.counterimages.digit))

        self.set_value(0)
        self.shoulddraw = True

    def set_value(self, value):
        counterstr = ("{:>"+str(self.counterlength)+"}").format(value)
        if len(counterstr) > len(self.digits):
            if value > 0:
                counterstr = '9'*len(self.digits)
            else:
                counterstr = '-'+'9'*(len(self.digits)-1)
        self.counterstr = counterstr
        ret = False
        for i, c in enumerate(self.counterstr):
            ret |= self.digits[i].set_value(c)
        return ret

    def draw(self, force):
        self.border.draw(force)
        for digit in self.digits:
            digit.draw(force)

class Digit:
    def __init__(self, displaycanvas, position, digitimages):
        self.displaycanvas = displaycanvas
        self.position = position
        self.digitimages = digitimages

        self.mapping = {
            ' ': 'off',
            '-': '-',
        }
        for i in range(10):
            self.mapping[str(i)] = i

        self.state = 0
        self.shoulddraw = True

    def set_value(self, value):
        if self.state != self.mapping[value]:
            self.state = self.mapping[value]
            self.shoulddraw = True
            return True
        return False

    def draw(self, force):
        if not (force or self.shoulddraw):
            return
        self.shoulddraw = False
        self.displaycanvas.paste(self.digitimages.i[self.state], self.position)

class Face:
    def __init__(self, displaycanvas, position, faceimages):
        self.displaycanvas = displaycanvas
        self.position = position
        self.faceimages = faceimages
        self.face = FaceState.Happy

        self.mapping = {
            FaceState.Happy:   'happy',
            FaceState.Pressed: 'pressed',
            FaceState.Blast:   'blast',
            FaceState.Cool:    'cool',
            FaceState.Nervous: 'nervous',
        }

        self.shoulddraw = True

    def set_face(self, face):
        if self.face != face:
            self.face = face
            self.shoulddraw = True
            return True
        return False

    def draw(self, force):
        if not (force or self.shoulddraw):
            return
        self.shoulddraw = False
        self.displaycanvas.paste(self.faceimages.i[self.mapping[self.face]], self.position)

class Board:
    def __init__(self, displaycanvas, position, boardimages, size, boardsize):
        self.displaycanvas = displaycanvas
        self.position = position
        self.boardimages = boardimages
        self.boardsize = boardsize
        self.size = size
        self.boardpixelsize = self.boardimages.getsize(boardsize)

        self.state = [[TileState.Unopened for i in range(self.boardsize[0])] for i in range(self.boardsize[1])]

        self.bganchor = (
            self.position[0] + self.size[0] // 2,
            self.position[1],
        )
        self.bgamount = (
            math.ceil(self.size[0] / self.boardimages.bg.size[0]),
            math.ceil(self.size[1] / self.boardimages.bg.size[1]),
        )
        self.bgpos = (
            self.bganchor[0] - self.bgamount[0] * self.boardimages.bg.size[0] // 2,
            self.bganchor[1],
        )
        self.bg = GridTile(self.displaycanvas, self.bgpos, self.bgamount, self.boardimages.bg)

        self.boardposition = (
            self.position[0] + (self.size[0] - self.boardpixelsize[0]) // 2,
            self.position[1],
        )
        self.border = Border(self.displaycanvas, self.boardposition, self.boardpixelsize, self.boardimages.border)

        self.tiles = [[None for i in range(self.boardsize[0])] for i in range(self.boardsize[1])]
        for col in range(self.boardsize[0]):
            for row in range(self.boardsize[1]):
                pos = (
                    self.boardposition[0] + self.boardimages.border.thickness[1] + col * self.boardimages.tile.size[0],
                    self.boardposition[1] + self.boardimages.border.thickness[0] + row * self.boardimages.tile.size[1],
                )
                self.tiles[row][col] = Tile(self.displaycanvas, pos, self.boardimages.tile)

        self.shoulddraw = True
        self.tileschanged = set((row, col) for col in range(self.boardsize[0]) for row in range(self.boardsize[1]))

    def set_tile(self, index, tile):
        """
        index is a 2-tuple containing the row and col of the tile to be modified.
        """
        if self.state[index[0]][index[1]] != tile:
            self.shoulddraw = True
            self.state[index[0]][index[1]] = tile
            self.tiles[index[0]][index[1]].set_tile(tile)
            self.tileschanged.add((index[0], index[1]))
            return True
        return False

    def draw(self, force):
        if not (force or self.shoulddraw):
            return
        self.shoulddraw = False

        self.bg.draw(force)
        self.border.draw(force)

        for row, col in self.tileschanged:
            self.tiles[row][col].draw(force)

        self.tileschanged = set()

class Tile:
    def __init__(self, displaycanvas, position, tileimages):
        self.displaycanvas = displaycanvas
        self.position = position
        self.tileimages = tileimages

        self.state = TileState.Unopened

        self.mapping = {
            TileState.Mine:      'mine',
            TileState.Blast:     'blast',
            TileState.Flag:      'flag',
            TileState.FlagWrong: 'flag_wrong',
            TileState.Unopened:  'unopened',
        }
        for i in range(9):
            self.mapping[TileState.Number[i]] = i

        self.shoulddraw = True

    def set_tile(self, tile):
        self.shoulddraw = True
        self.state = tile

    def draw(self, force):
        if not (force or self.shoulddraw):
            return
        self.shoulddraw = True
        self.displaycanvas.paste(self.tileimages.i[self.mapping[self.state]], self.position)
