

class Line(object):

    def __init__(self, x1, y1, x2, y2):
        # TODO: add asserts
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.v1 = x2 - x1
        self.v2 = y2 - y1
        self.length_sq = float(self.v1 * self.v1 + self.v2 * self.v2)
