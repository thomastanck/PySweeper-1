class Part:
    """
    Models the individual parts of the screen in terms of a bounding box.
    This is used to transform coordinates (Pos) between different skins and
    also aids in the click processing to determine where the mouse is.

    (0, 0) is the top left of the PySweeper window.
    """
    def __init__(self, name, parent, rootoffset, size):
        self.name = name
        self.parent = parent
        self.rootoffset = rootoffset
        self.size = size
        self.children = {}
        if parent == None:
            self.partspec = (self.name,)
        else:
            self.partspec = self.parent.partspec + (self.name,)

    def add_child(self, otherpart):
        self.children[otherpart.name] = otherpart

    def is_child_of(self, otherpart):
        if self == otherpart:
            return True
        else:
            return self.parent.is_child_of(otherpart)

    def __contains__(self, coord):
        return self.contains(coord)

    def contains(self, coord):
        return (self.rootoffset[0] <= coord[0] < self.rootoffset[0] + self.size[0] and
            self.rootoffset[1] <= coord[1] < self.rootoffset[1] + self.size[1])


def _find_part(coord, in_part):
    """
    This function returns the deepest part that contains the coordinate coord.
    This is done because parents overlap children, so before we decide that the
    coordinate is in a certain part, we have to check if the part is in any of
    its children parts.
    """
    for part in in_part.children.values():
        if part.contains(coord):
            return _find_part(coord, in_part)
    else:
        # none of the parts contained the coord.
        return in_part

class Pos:
    """
    Basically a coordinate with convenience functions.

    (0, 0) is the top left of the PySweeper window.

    root is the Part associated with the PySweeper window.
    """
    def __init__(self, coord, root):
        self.coord = coord
        self.root = root

        self.part = _find_part(self.coord, self.root)

    def in_part(self, part):
        """
        Returns true if the pos is over the part and not over any of its
        children.
        """
        return self.part == part

    def transform(self, newroot):
        """
        This function attempts to find the equivalent part in the new root
        and map its coords to the coords in the equivalent part.
        """
        newpart = newroot
        for partname in self.part.partspec:
            newpart = newpart.children[partname]
        assert(newpart.partspec == self.part.partspec)

        normalised = (
            (self.coord[0] - self.part.rootoffset[0]) / self.part.size[0],
            (self.coord[1] - self.part.rootoffset[1]) / self.part.size[1],
        )
        newcoord = (
            normalised[0] * newpart.size[0] + newpart.rootoffset[0],
            normalised[1] * newpart.size[1] + newpart.rootoffset[1],
        )

class Pos:
    """
    A class that contains coordinates and lots of fancy stuff to help
    translate/transform them into local coordinates rooted on a part of the
    display/etc.

    (offsetx + x, offsety + y) will represent a point on the pysweeper window
    starting on the top left of the window.
    """
    def __init__(self, *args):
        # Consume 2-tuples or 2 args until we have x/y, offset, and size.
        if type(args[0]) == tuple:
            self.x, self.y = args[0]
            args = args[1:]
        else:
            self.x, self.y = args[0:2]
            args = args[2:]

        self.offsetx, self.offsety = (0, 0)
        if len(args) > 0:
            if type(args[0]) == tuple:
                self.offsetx, self.offsety = args[0]
                args = args[1:]
            else:
                self.offsetx, self.offsety = args[0:2]
                args = args[2:]

        self.sizex, self.sizey = (0, 0)
        if len(args) > 0:
            if type(args[0]) == tuple:
                self.sizex, self.sizey = args[0]
            else:
                self.sizex, self.sizey = args[0:2]
