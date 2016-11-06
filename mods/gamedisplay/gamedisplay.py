import math
from collections import OrderedDict

from PIL import Image, ImageTk
import tkinter

from gamedisplay.displayimages import DisplayImages
from gamedisplay.event import DisplayEvent
from gamedisplay.state import TileState, FaceState

import pysweep.pos as pos
import pysweep.mod as mod
# from pysweep.event import Event

class GameDisplay(mod.Mod):
    def __init__(self):
        # Expose the state enums for other mods to see and use
        self.TileState = TileState
        self.FaceState = FaceState

        self.boardsize = (30, 16)
        self.lcounterlength = 3
        self.rcounterlength = 3

        self.images = DisplayImages('images')

    def pysweep_before_finish_init(self):
        """
        Create and show the display on the screen.

        After that, obtain the positions for all the parts in the display so
        other mods (namely ClickManager) can figure out where mouse events
        are.
        """
        self.displaycanvas = DisplayCanvas(self.pysweep.master, self.boardsize, self.lcounterlength, self.rcounterlength, self.images)
        self.displaycanvas.pack()

        self.pysweep.master.update_idletasks()
        self.displaycanvas.update_idletasks()
        # enode = self.arbitrary()
        # print('DisplayCanvas:', enode)

    # @mod.trigger
    # def arbitrary(self):
    #     return None, Event()

    # @mod.listen('GameDisplay', 'arbitrary')
    # def listener(self, event):
    #     self.set_rcounter(event, 0)

    def set_lcounter(self, event, value):
        if self.displaycanvas.set_lcounter(value):
            self.on_set_lcounter(event, value)
            self.displaycanvas.draw()
    def set_face(self, event, face):
        if self.displaycanvas.set_face(face):
            self.on_set_face(event, face)
            self.displaycanvas.draw()
    def set_rcounter(self, event, value):
        if self.displaycanvas.set_rcounter(value):
            self.on_set_rcounter(event, value)
            self.displaycanvas.draw()
    def set_tile(self, event, index, tile):
        if self.displaycanvas.set_tile(index, tile):
            self.on_set_tile(event, index, tile)
            self.displaycanvas.draw()

    def get_lcounter(self):
        return self.displaycanvas.get_lcounter()
    def get_face(self):
        return self.displaycanvas.get_face()
    def get_rcounter(self):
        return self.displaycanvas.get_rcounter()
    def get_tile(self, index):
        return self.displaycanvas.get_tile(index)

    @mod.trigger
    def on_set_lcounter(self, event, value):
        return event, DisplayEvent('lcounter', value)
    @mod.trigger
    def on_set_face(self, event, face):
        return event, DisplayEvent('face', face)
    @mod.trigger
    def on_set_rcounter(self, event, value):
        return event, DisplayEvent('rcounter', value)
    @mod.trigger
    def on_set_tile(self, event, index, tile):
        return event, DisplayEvent('tile', index, tile)

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

        self.img = Image.new(size=self.size, mode="RGBA", color='green')
        self.tkimg = ImageTk.PhotoImage(self.img)
        self.create_image(0, 0, image=self.tkimg, anchor='nw')

        self.display = Display.new(self, (0, 0), images, boardsize, lcounterlength, rcounterlength)

        self.draw()
        # self.img.paste(Image.new(size=self.size, mode="RGBA", color='blue'))
        # self.draw()

    def set_lcounter(self, value):
        return self.display.set_lcounter(value)
    def set_face(self, face):
        return self.display.set_face(face)
    def set_rcounter(self, value):
        return self.display.set_rcounter(value)
    def set_tile(self, index, tile):
        return self.display.set_tile(index, tile)

    def get_lcounter(self):
        return self.display.get_lcounter()
    def get_face(self):
        return self.display.get_face()
    def get_rcounter(self):
        return self.display.get_rcounter()
    def get_tile(self, index):
        return self.display.get_tile(index)

    def paste(self, img, pos):
        self.img.paste(img, pos, img)
        self.update()
    def paste_pixel(self, col, pos):
        self.img.paste(col, pos)
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
        self.display.draw(force)

    def update(self):
        if not self.update_queued:
            self.update_queued = True
            self.master.after(0, self.actually_update)

    def actually_update(self):
        self.update_queued = False
        self.tkimg.paste(self.img)

class Part:
    """
    Parent class for all the parts. This class stores the position, and sizes of
    itself, as well as an dict of its children. The classes which actually
    draw stuff will inherit this class.

    The only exception is Border, which is actually a group of 8 GridTile parts.
    Since that's the only case where parts don't nest nicely, I've decided not
    to make a separate class for groups of parts and just have Border return
    its children in an array.
    """
    def __init__(self, displaycanvas, position, size):
        self.displaycanvas = displaycanvas
        self.position = position
        self.size = size

        self.ignore = False # If set to true, then this will not be included in
                            # a get_part_containing search.

        # We use a collections.OrderedDict because we want to redraw parts
        # in a certain order. The best way is probably to retain the order
        # they were inserted so that the subclasses can choose the redraw order.
        self.children = OrderedDict()

    def draw(self, force=False):
        """
        Call this to trigger an update (lazily)
        Call with True to force a redraw of all its children
        """
        for child in self.children.values():
            child.draw(force)

    def contains(self, coord):
        """
        Returns True if the coord is in Part or any of its children.
        May be a better idea to call the get_part_containing function instead
        though, which returns the lowest level Part that contains the coord
        (none of its children contain the coord, but the Part does)
        """
        # print(coord, self.position, self.size)
        return (0 <= coord[0] - self.position[0] < self.size[0] and
                0 <= coord[1] - self.position[1] < self.size[1])

    def get_part_containing(self, coord):
        """
        Returns the lowest Part that contains the coord (a part that contains
        the coord where none of its children contain the coord)

        *** Assumes that self already contains coord! Please check this if you
        are not sure! ***
        """
        # print('in', self)
        for k, child in self.children.items():
            # print('try', k, child)
            if child.ignore:
                # print('ignore', k, child)
                continue
            if child.contains(coord):
                # print('contained', k, child)
                return child.get_part_containing(coord)
        # Could not find any children containing the coord, so we must be at the
        # lowest level already
        return self

class Drawable(Part):
    """
    Parent class for all parts that actually do drawing as opposed to internal
    parts in the parts tree (such as Panel, which only handles its children but
    does not actually draw anything)
    """
    def __init__(self, displaycanvas, position, size):
        Part.__init__(self, displaycanvas, position, size)
        self.shoulddraw = True

    def draw(self, force):
        if self.shoulddraw or force:
            self.shoulddraw = False
            self._draw()
    def _draw(self):
        raise NotImplementedError("_draw must be imlemented for all Drawable's.")

class GridTile(Drawable):
    """
    Repeatedly pastes an image a number of times in two directions.

    It will try to paste the image to fit the size provided, but if size isn't
    divisible by the image dimensions, it will overflow.
    """
    class PasteType:
        class Pixel: pass # Optimisation for when the image itself is 1x1
        class Once: pass # Optimisation for when image is as big/bigger than the paste size
        class Horz: pass # Optimisation for when image is 1xh (resize width)
        class Vert: pass # Optimisation for when image is wx1 (resize height)
        class Tile: pass # The usual

    def __init__(self, displaycanvas, position, size, img):
        Drawable.__init__(self, displaycanvas, position, size)

        PasteType = GridTile.PasteType

        self.img = img

        imgsize = self.img.size
        self.imgsize = imgsize

        self.paste_amounts = (
            math.ceil(size[0] / imgsize[0]),
            math.ceil(size[1] / imgsize[1]),
        )

        if imgsize == (1, 1):
            self.pastetype = PasteType.Pixel
            self.pixel = img.getpixel((0,0))
        elif imgsize[0] >= size[0] and imgsize[1] >= size[1]:
            self.pastetype = PasteType.Once
        elif imgsize[0] == 1:
            self.pastetype = PasteType.Horz
            newsize = (self.paste_amounts[0], imgsize[1])
            self.img = self.img.resize(newsize)
        elif imgsize[1] == 1:
            self.pastetype = PasteType.Vert
            newsize = (imgsize[0], self.paste_amounts[1])
            self.img = self.img.resize(newsize)
        else:
            self.pastetype = PasteType.Tile

    def _draw(self):
        PasteType = GridTile.PasteType

        if self.pastetype == PasteType.Pixel:
            pastearea = (
                self.position[0],
                self.position[1],
                self.position[0] + self.paste_amounts[0],
                self.position[1] + self.paste_amounts[1],
            )
            self.displaycanvas.paste_pixel(self.pixel, pastearea)
        elif self.pastetype == PasteType.Once:
            self.displaycanvas.paste(self.img, self.position)
        elif self.pastetype == PasteType.Horz:
            for row in range(self.paste_amounts[1]):
                pastepos = (
                    self.position[0],
                    self.position[1] + self.imgsize[1] * row,
                )
                self.displaycanvas.paste(self.img, pastepos)
        elif self.pastetype == PasteType.Vert:
            for col in range(self.paste_amounts[0]):
                pastepos = (
                    self.position[0] + self.imgsize[0] * col,
                    self.position[1],
                )
                self.displaycanvas.paste(self.img, pastepos)
        else:
            for col in range(self.paste_amounts[0]):
                for row in range(self.paste_amounts[1]):
                    pastepos = (
                        self.position[0] + self.imgsize[0] * col,
                        self.position[1] + self.imgsize[1] * row,
                    )
                    self.displaycanvas.paste(self.img, pastepos)

class Border:
    """
    Draws a box border using the 8 images provided.
    """
    def __init__(self, displaycanvas, position, size, images):
        self.parts = {}

        insize = (
            size[0] - images.size[0],
            size[1] - images.size[1],
        )

        th, lw, rw, bh = images.thickness

        # Edges
        guide = {
            't': [(position[0] + lw + 0,         position[1] + 0),              (math.ceil(insize[0] / images.i['t'].size[0]), th)],
            'b': [(position[0] + lw + 0,         position[1] + th + insize[1]), (math.ceil(insize[0] / images.i['b'].size[0]), bh)],
            'l': [(position[0] + 0,              position[1] + th + 0),         (lw, math.ceil(insize[1] / images.i['l'].size[1]))],
            'r': [(position[0] + lw + insize[0], position[1] + th + 0),         (rw, math.ceil(insize[1] / images.i['r'].size[1]))],
        }
        for k, v in guide.items():
            self.parts[k] = GridTile(displaycanvas, v[0], v[1], images.i[k])

        # Corners
        guide = {
            'tl': (position[0] + 0,              position[1] + 0),
            'tr': (position[0] + lw + insize[0], position[1] + 0),
            'bl': (position[0] + 0,              position[1] + th + insize[1]),
            'br': (position[0] + lw + insize[0], position[1] + th + insize[1]),
        }
        for k, v in guide.items():
            self.parts[k] = GridTile(displaycanvas, v, images.i[k].size, images.i[k])

class Display(Part):
    """
    The part representing the entire display. To draw the entire pysweeper
    display onto a canvas, just instantiate this class with a PIL image, and
    then call display.draw() to trigger all the pastes.
    """
    @classmethod
    def new(cls, displaycanvas, position, images, boardsize=(30, 16), lcounterlength=3, rcounterlength=3):
        size = images.getsize(boardsize, lcounterlength, rcounterlength)
        return cls(displaycanvas, position, size, images, boardsize, lcounterlength, rcounterlength)

    def __init__(self, displaycanvas, position, size, images, boardsize, lcounterlength, rcounterlength):
        Part.__init__(self, displaycanvas, position, size)
        self.images = images
        self.boardsize = boardsize
        self.lcounterlength = lcounterlength
        self.rcounterlength = rcounterlength

        # Takes the max of the panel width and board width.
        displaywidth = self.images.getinsize(self.boardsize, self.lcounterlength, self.rcounterlength)[0]

        # Position/size of border
        borderpos = self.position
        bordersize = self.size

        # Position/size of panel
        panelpos = (
            position[0] + self.images.border.thickness[1],
            position[1] + self.images.border.thickness[0],
        )
        panelsize = (
            displaywidth,
            self.images.panel.getsize(lcounterlength, rcounterlength)[1],
        )

        # Position/size of board
        boardpos = (
            position[0] + self.images.border.thickness[1],
            position[1] + self.images.border.thickness[0] + panelsize[1],
        )
        boardpixelsize = (
            displaywidth,
            self.images.board.getsize(boardsize)[1],
        )

        border = Border(self.displaycanvas, borderpos, bordersize, self.images.border)
        panel = Panel(self.displaycanvas, panelpos, panelsize, self.images.panel, self.lcounterlength, self.rcounterlength)
        board = Board(self.displaycanvas, boardpos, boardpixelsize, self.images.board, self.boardsize)

        for k, v in border.parts.items():
            self.children[k] = v
        self.children['panel'] = panel
        self.children['board'] = board

class Panel(Part):
    def __init__(self, displaycanvas, position, size, images, lcounterlength, rcounterlength):
        Part.__init__(self, displaycanvas, position, size)
        self.images = images
        self.lcounterlength = lcounterlength
        self.rcounterlength = rcounterlength

        insize = (
            self.size[0] - self.images.border.size[0],
            self.size[1] - self.images.border.size[1],
        )

        # Background
        bganchor = (
            self.position[0] + self.size[0] // 2,
            self.position[1] + self.images.border.thickness[0],
        )
        bgsize = (
            self.size[0] - self.images.border.size[0],
            self.size[1] - self.images.border.size[1],
        )
        bgamount = (
            math.ceil(insize[0] / self.images.bg.size[0]),
            math.ceil(insize[1] / self.images.bg.size[1]),
        )
        bgpos = (
            bganchor[0] - bgamount[0] * self.images.bg.size[0] // 2,
            bganchor[1],
        )

        # Border
        borderpos = self.position
        bordersize = self.size

        # Left counter
        lcounterpos = (
            self.position[0] + self.images.border.thickness[1],
            self.position[1] + self.images.border.thickness[0],
        )

        # Face
        facepos = (
            self.position[0] + (self.size[0] - self.images.face.size[0]) // 2,
            self.position[1] + self.images.border.thickness[0],
        )

        # Right counter
        rcounterpos = (
            self.position[0] + self.size[0] - self.images.border.thickness[2] - self.images.rcounter.getsize(rcounterlength)[0],
            self.position[1] + self.images.border.thickness[0],
        )

        bg = GridTile(self.displaycanvas, bgpos, bgsize, self.images.bg)
        border = Border(self.displaycanvas, borderpos, bordersize, self.images.border)
        lcounter = Counter.new(self.displaycanvas, lcounterpos, self.images.lcounter, lcounterlength)
        face = Face.new(self.displaycanvas, facepos, self.images.face)
        rcounter = Counter.new(self.displaycanvas, rcounterpos, self.images.rcounter, rcounterlength)

        bg.ignore = True
        self.children['bg'] = bg
        for k, v in border.parts.items():
            self.children[k] = v
        self.children['lcounter'] = lcounter
        self.children['face'] = face
        self.children['rcounter'] = rcounter

class Board(Part):
    def __init__(self, displaycanvas, position, size, images, boardsize):
        Part.__init__(self, displaycanvas, position, size)
        self.images = images
        self.boardsize = boardsize

        insize = self.images.getinsize(boardsize)

        # Background
        bganchor = (
            self.position[0] + self.size[0] // 2,
            self.position[1] + self.images.border.thickness[0],
        )
        bgsize = (
            self.size[0] - self.images.border.size[0],
            self.size[1] - self.images.border.size[1],
        )
        bgamount = (
            math.ceil(insize[0] / self.images.bg.size[0]),
            math.ceil(insize[1] / self.images.bg.size[1]),
        )
        bgpos = (
            bganchor[0] - bgamount[0] * self.images.bg.size[0] // 2,
            bganchor[1],
        )

        # Border
        borderpos = self.position
        bordersize = self.size

        # Board
        boardpos = (
            self.position[0] + self.images.border.thickness[1] + (self.size[0] - self.images.getsize(self.boardsize)[0]) // 2,
            self.position[1] + self.images.border.thickness[0],
        )

        bg = GridTile(self.displaycanvas, bgpos, bgsize, self.images.bg)
        border = Border(self.displaycanvas, borderpos, bordersize, self.images.border)
        tiles = BoardTiles(self.displaycanvas, boardpos, insize, self.images.tile, self.boardsize)

        bg.ignore = True
        self.children['bg'] = bg
        for k, v in border.parts.items():
            self.children[k] = v
        self.children['tiles'] = tiles

class Counter(Part):
    @classmethod
    def new(cls, displaycanvas, position, images, counterlength):
        size = images.getsize(counterlength)
        return cls(displaycanvas, position, size, images, counterlength)

    def __init__(self, displaycanvas, position, size, images, counterlength):
        Part.__init__(self, displaycanvas, position, size)
        self.images = images
        self.counterlength = counterlength

        # Border
        borderpos = self.position
        bordersize = self.size

        self.border = Border(self.displaycanvas, borderpos, bordersize, self.images.border)
        self.digits = []
        for i in range(counterlength):
            digitpos = (
                self.position[0] + self.images.border.thickness[1] + self.images.digit.size[0] * i,
                self.position[1] + self.images.border.thickness[0],
            )
            self.digits.append(Digit.new(self.displaycanvas, digitpos, self.images.digit))

        self.set_value(0)
        # Don't add digits to children, so if Part.get_part_containing(self, coord)
        # is called, the search stops here and Counter is returned.

    def draw(self, force=False):
        for borderpart in self.border.parts.values():
            borderpart.draw(force)
        for digit in self.digits:
            digit.draw(force)
        self.tileschanged = set()

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

    def get_value(self):
        return counterstr


class Digit(Drawable):
    @classmethod
    def new(cls, displaycanvas, position, images):
        size = images.size
        return cls(displaycanvas, position, size, images)

    def __init__(self, displaycanvas, position, size, images):
        Drawable.__init__(self, displaycanvas, position, size)
        self.images = images

        self.mapping = {
            ' ': 'off',
            '-': '-',
        }
        for i in range(10):
            self.mapping[str(i)] = i

        self.state = 0

    def set_value(self, value):
        if self.state != self.mapping[value]:
            self.state = self.mapping[value]
            self.shoulddraw = True
            return True
        return False

    def _draw(self):
        self.displaycanvas.paste(self.images.i[self.state], self.position)

class Face(Drawable):
    @classmethod
    def new(cls, displaycanvas, position, images):
        size = images.size
        return cls(displaycanvas, position, size, images)

    def __init__(self, displaycanvas, position, size, images):
        Drawable.__init__(self, displaycanvas, position, size)
        self.images = images
        self.face = FaceState.Happy

        self.mapping = {
            FaceState.Happy:   'happy',
            FaceState.Pressed: 'pressed',
            FaceState.Blast:   'blast',
            FaceState.Cool:    'cool',
            FaceState.Nervous: 'nervous',
        }

    def set_face(self, face):
        if self.face != face:
            self.face = face
            self.shoulddraw = True
            return True
        return False

    def get_face(self, face):
        return self.face

    def _draw(self):
        self.displaycanvas.paste(self.images.i[self.mapping[self.face]], self.position)

class BoardTiles(Part):
    def __init__(self, displaycanvas, position, size, images, boardsize):
        Part.__init__(self, displaycanvas, position, size)
        self.images = images
        self.boardsize = boardsize

        self.tiles = [[None for i in range(self.boardsize[0])] for i in range(self.boardsize[1])]
        for col in range(self.boardsize[0]):
            for row in range(self.boardsize[1]):
                pos = (
                    self.position[0] + col * self.images.size[0],
                    self.position[1] + row * self.images.size[1],
                )
                self.tiles[row][col] = Tile.new(self.displaycanvas, pos, self.images)

        self.tileschanged = set((row, col) for col in range(self.boardsize[0]) for row in range(self.boardsize[1]))

        # Don't add tiles to children, so if Part.get_part_containing(self, coord)
        # is called, the search stops here and BoardTiles is returned, as opposed
        # to searching within our tiles array and seeing which tile got clicked,
        # which would only be more annoying to figure out.

    def draw(self, force=False):
        for row, col in self.tileschanged:
            self.tiles[row][col].draw(force)
        self.tileschanged = set()

class Tile(Drawable):
    @classmethod
    def new(cls, displaycanvas, position, images):
        size = images.size
        return cls(displaycanvas, position, size, images)

    def __init__(self, displaycanvas, position, size, images):
        Drawable.__init__(self, displaycanvas, position, size)
        self.images = images

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

    def set_tile(self, tile):
        self.state = tile
        self.shoulddraw = True

    def _draw(self):
        self.displaycanvas.paste(self.images.i[self.mapping[self.state]], self.position)
