class TileState:
    """
    poor man's enum for a tile's state

    This is because actual enums either need an external pip package or
    Python 3.4+
    """
    class Mine: pass
    class Blast: pass
    class Flag: pass
    class FlagWrong: pass
    class Unopened: pass
    # A bit of magic to create 9 classes of 'Number' in an array
    # You use this like TileState.Number[i] where i=0..8
    Number = [type('Number_{}'.format(i), (), {}) for i in range(9)]

class FaceState:
    """
    poor man's enum for the face's state

    This is because actual enums either need an external pip package or
    Python 3.4+
    """
    class Happy: pass
    class Pressed: pass
    class Blast: pass
    class Cool: pass
    class Nervous: pass
