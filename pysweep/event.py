class Event:
    """
    Supposed to be some parent class or something. "saa..."
    """
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.children = []

    def __str__(self):
        return "\{args:{},kwargs:{},children:{}\}".format(
            self.args,
            self.kwargs,
            self.children
        )

    def __repr__(self):
        return self.__str__()
