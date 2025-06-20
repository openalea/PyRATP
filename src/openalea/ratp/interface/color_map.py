class ColorMap:
    """A RGB color map, between 2 colors defined in HSV code
    """

    def __init__(self, minval=0., maxval=1.):
        self.minval = float(minval)
        self.maxval = float(maxval)

    def color(self, normedU):
        """

        :param normedU: todo

        """
        inter = 1 / 5.
        winter = int(normedU / inter)
        a = (normedU % inter) / inter
        b = 1 - a

        if winter < 0:
            col = (self.coul2, self.coul2, self.coul1)
        elif winter == 0:
            col = (self.coul2, self.coul2 * b + self.coul1 * a, self.coul1)
        elif winter == 1:
            col = (self.coul2, self.coul1, self.coul1 * b + self.coul2 * a)
        elif winter == 2:
            col = (self.coul2 * b + self.coul1 * a, self.coul1, self.coul2)
        elif winter == 3:
            col = (self.coul1, self.coul1 * b + self.coul2 * a, self.coul2)
        elif winter > 3:
            col = (self.coul1, self.coul2, self.coul2)
        return (int(col[0]), int(col[1]), int(col[2]))

    def greycolor(self, normedU):
        """

        :param normedU: todo
        :returns: todo
        """
        return (int(255 * normedU), int(255 * normedU), int(255 * normedU))

    def grey(self, u):
        """
        :param u:
        :returns: todo
        """
        return self.greycolor(self.normU(u))

    def normU(self, u):
        """
        :param u:
        :returns: todo
        """
        if self.minval == self.maxval:
            return 0.5
        return (u - self.minval) / (self.maxval - self.minval)

    def __call__(self, u, minval=0, maxval=1, coul1=80, coul2=20):
        self.coul1 = coul1
        self.coul2 = coul2
        self.minval = float(minval)
        self.maxval = float(maxval)
        return self.color(self.normU(u))
