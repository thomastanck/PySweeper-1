import os

from PIL import Image

class DisplayImages:
    """
    Object that contains all the images needed to display the board.

    Comes with convenience functions to load them from disk :>
    """
    def __init__(self, image_dir, default_image_dir='images'):
        self.image_dir = image_dir
        self.default_image_dir = default_image_dir # Used if image isn't found in image_dir

        self.border = BorderImages(os.path.join(image_dir, 'border'), os.path.join(default_image_dir, 'border'))
        self.panel =  PanelImages( os.path.join(image_dir, 'panel'),  os.path.join(default_image_dir, 'panel'))
        self.board =  BoardImages( os.path.join(image_dir, 'board'),  os.path.join(default_image_dir, 'board'))

class BorderImages:
    """
    All the borders of a certain part.
    """
    def __init__(self, image_dir, default_image_dir):
        self.image_dir = image_dir
        self.default_image_dir = default_image_dir # Used if image isn't found in image_dir

        self.thickness = [None]*4 # Top, Left, Right, Bottom border thickness

        self.i = {}

        self.keys = [
            'tl', 't', 'tr',
            'l',       'r',
            'bl', 'b', 'br',
        ]
        for key in self.keys:
            try:
                imgpath = os.path.join(self.image_dir, "{}.png".format(key))
                img = Image.open(imgpath)
            except:
                imgpath = os.path.join(self.default_image_dir, "{}.png".format(key))
                img = Image.open(imgpath)
            self.i[key] = img

        # Check top size
        for key in 'tl', 't', 'tr':
            if self.thickness[0] == None:
                self.thickness[0] = self.i[key].size[1]
            else:
                try:
                    assert self.thickness[0] == self.i[key].size[1]
                except AssertionError as e:
                    e.args += (' '.join([
                        "All borders must have consistent thickness.",
                        "Expected height {}".format(self.thickness[0]),
                        "but '{}'".format(imgpath),
                        "has height {}.".format(self.i[key].size[1]),
                    ]),)
                    raise e
        # Check left size
        for key in 'tl', 'l', 'bl':
            if self.thickness[1] == None:
                self.thickness[1] = self.i[key].size[0]
            else:
                try:
                    assert self.thickness[1] == self.i[key].size[0]
                except AssertionError as e:
                    e.args += (' '.join([
                        "All borders must have consistent thickness.",
                        "Expected width {}".format(self.thickness[1]),
                        "but '{}'".format(imgpath),
                        "has width {}.".format(self.i[key].size[0]),
                    ]),)
                    raise e
        # Check right size
        for key in 'tr', 'r', 'br':
            if self.thickness[2] == None:
                self.thickness[2] = self.i[key].size[0]
            else:
                try:
                    assert self.thickness[2] == self.i[key].size[0]
                except AssertionError as e:
                    e.args += (' '.join([
                        "All borders must have consistent thickness.",
                        "Expected width {}".format(self.thickness[1]),
                        "but '{}'".format(imgpath),
                        "has width {}.".format(self.i[key].size[0]),
                    ]),)
                    raise e
        # Check bottom size
        for key in 'bl', 'b', 'br':
            if self.thickness[3] == None:
                self.thickness[3] = self.i[key].size[1]
            else:
                try:
                    assert self.thickness[3] == self.i[key].size[1]
                except AssertionError as e:
                    e.args += (' '.join([
                        "All borders must have consistent thickness.",
                        "Expected height {}".format(self.thickness[3]),
                        "but '{}'".format(imgpath),
                        "has height {}.".format(self.i[key].size[1]),
                    ]),)
                    raise e

        self.thickness = tuple(self.thickness)
        self.size = (self.thickness[1]+self.thickness[2], self.thickness[0]+self.thickness[3])

    def __getattr__(self, key):
        if key in self.keys:
            return self.i[key]
        else:
            raise KeyError('{} is not a member of {}'.format(key, self))

class PanelImages:
    """
    All the images in the panel.
    """
    def __init__(self, image_dir, default_image_dir):
        self.image_dir = image_dir
        self.default_image_dir = default_image_dir # Used if image isn't found in image_dir

        self.border =   BorderImages( os.path.join(image_dir, 'border'),   os.path.join(default_image_dir, 'border'))
        self.lcounter = CounterImages(os.path.join(image_dir, 'lcounter'), os.path.join(default_image_dir, 'lcounter'))
        self.face =     FaceImages(   os.path.join(image_dir, 'face'),     os.path.join(default_image_dir, 'face'))
        self.rcounter = CounterImages(os.path.join(image_dir, 'rcounter'), os.path.join(default_image_dir, 'rcounter'))

        # The background
        try:
            imgpath = os.path.join(self.image_dir, "bg.png")
            img = Image.open(imgpath)
        except:
            imgpath = os.path.join(self.default_image_dir, "bg.png")
            img = Image.open(imgpath)

        self.i = {'bg': img}
        self.bg = img

    def getsize(self, lcounter_length=1, rcounter_length=None):
        lcountersize = self.lcounter.getsize(lcounter_length)
        if rcounter_length is None:
            rcountersize = self.lcounter.getsize(lcounter_length)
        else:
            rcountersize = self.lcounter.getsize(rcounter_length)
        return (
            self.border.size[0] + lcountersize[0] + self.face.size[0] + rcountersize[0],
            self.border.size[1] + max(lcountersize[1], self.face.size[1], rcountersize[1]),
        )
    @property
    def size(self):
        return self.getsize()

class CounterImages:
    """
    All the images in the counter.
    """
    def __init__(self, image_dir, default_image_dir):
        self.image_dir = image_dir
        self.default_image_dir = default_image_dir # Used if image isn't found in image_dir

        self.border = BorderImages(os.path.join(image_dir, 'border'), os.path.join(default_image_dir, 'border'))
        self.digit =  DigitImages( os.path.join(image_dir, 'digit'),  os.path.join(default_image_dir, 'digit'))

    def getsize(self, counter_length=1):
        return (
            self.border.size[0] + self.digit.size[0] * counter_length,
            self.border.size[1] + self.digit.size[1] * counter_length,
        )
    @property
    def size(self):
        return self.getsize()

class SpriteImages:
    """
    Loads identically sized images.
    """
    def __init__(self, keys, image_dir, default_image_dir):
        self.keys = keys
        self.image_dir = image_dir
        self.default_image_dir = default_image_dir # Used if image isn't found in image_dir

        self.i = {}

        self.size = None
        for key in self.keys:
            try:
                imgpath = os.path.join(self.image_dir, "{}.png".format(key))
                img = Image.open(imgpath)
            except:
                imgpath = os.path.join(self.default_image_dir, "{}.png".format(key))
                img = Image.open(imgpath)
            self.i[key] = img

            if self.size == None:
                self.size = img.size
            else:
                try:
                    assert self.size == img.size
                except AssertionError as e:
                    e.args += (' '.join([
                        "All images of this type must be of same size.",
                        "Expected size ({}, {})".format(*self.size),
                        "but '{}'".format(imgpath),
                        "has size ({}, {}).".format(*img.size),
                    ]),)

                    raise e

class DigitImages(SpriteImages):
    """
    All the digits of a counter.
    """
    def __init__(self, image_dir, default_image_dir):
        self.keys = ['off', '-'] + list(range(10))
        SpriteImages.__init__(self, self.keys, image_dir, default_image_dir)

class FaceImages(SpriteImages):
    """
    All the faces.
    """
    def __init__(self, image_dir, default_image_dir):
        self.keys = ['happy', 'pressed', 'blast', 'cool', 'nervous']
        SpriteImages.__init__(self, self.keys, image_dir, default_image_dir)

    def __getattr__(self, key):
        if key in self.keys:
            return self.i[key]
        else:
            raise KeyError('{} is not a face image'.format(key, self))

class BoardImages:
    """
    All the images in the board.
    """
    def __init__(self, image_dir, default_image_dir):
        self.image_dir = image_dir
        self.default_image_dir = default_image_dir # Used if image isn't found in image_dir

        self.border = BorderImages(os.path.join(image_dir, 'border'), os.path.join(default_image_dir, 'border'))
        self.tile =   TileImages(  os.path.join(image_dir, 'tile'),   os.path.join(default_image_dir, 'tile'))

    def getsize(self, boardsize=(1,1)):
        return (
            self.border.size[0] + self.tile.size[0] * boardsize[0],
            self.border.size[1] + self.tile.size[1] * boardsize[1],
        )
    @property
    def size(self):
        return self.getsize()

class TileImages(SpriteImages):
    """
    All the faces.
    """
    def __init__(self, image_dir, default_image_dir):
        self.keys = list(range(9)) + ["unopened", "flag", "blast", "flag_wrong", "mine"]
        SpriteImages.__init__(self, self.keys, image_dir, default_image_dir)

        self.n = [self.i[n] for n in range(9)]

    def __getattr__(self, key):
        if key == self.keys:
            return self.i[key]
        else:
            raise KeyError('{} is not a tile image'.format(key, self))
