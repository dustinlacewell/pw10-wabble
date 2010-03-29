import math

import pyglet

from src.util import gradient

class Line(object):
    
    LENGTH = 30
    SPEED = 200
    HEATUP_RADIUS = 300
    
    gradient = gradient((1.0, 0.0, 0.0), (0.0, 0.0, 0.0), HEATUP_RADIUS)

    def __init__(self, scene, x1, y1, x2, y2):
        # TODO: add asserts
        assert(x1 <= x2)
        assert(y1 <= y2)
        
        self.scene = scene
        
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.v1 = x2 - x1
        self.v2 = y2 - y1
        self.length_sq = float(self.v1 * self.v1 + self.v2 * self.v2)
        # self.length = self.length_sq ** 0.5
        
    def draw(self):
        p = self.scene.player
        dist = math.sqrt(((self.x1 - p.x)**2) + ((self.y1 - p.y)**2))
        dist = int(min(self.HEATUP_RADIUS - 1, dist))
        color = list(self.gradient[dist])
        color.append(1.0)
        pyglet.gl.glColor4f(*color)
        pyglet.graphics.draw(2, pyglet.gl.GL_LINES,
             ('v2i', (int(self.x1), int(self.y1), int(self.x2), int(self.y2)))
        )
        
        
class HorizontalLine(Line):
    def __init__(self, scene, batch, y_pos):
        x1 = 0
        x2 = self.LENGTH
        y1 = y2 = y_pos
        super(HorizontalLine, self).__init__(scene, x1, y1, x2, y2)
        self.forward = True
        
    def __slot(self):
        return self.y1
    slot =property(__slot)
        
    def update(self, dt):
        if self.forward:
            pc = dt * self.SPEED
            self.x1 += pc
            self.x2 += pc
            if self.x2 >= 600:
                self.forward = False
                self.x1 = 600 - self.LENGTH
                self.x2 = 600
        else:
            pc = dt * self.SPEED
            self.x1 -= pc
            self.x2 -= pc
            if self.x1 <= 0:
                self.forward = True
                self.x1 = 0
                self.x2 = self.LENGTH
                
class VerticalLine(Line):
    def __init__(self, scene, batch, x_pos):
        y1 = 0
        y2 = self.LENGTH
        x1 = x2 = x_pos
        super(VerticalLine, self).__init__(scene, x1, y1, x2, y2)
        self.forward = True
        
    def __slot(self):
        return self.x1
    slot = property(__slot)
        
    def update(self, dt):
        if self.forward:
            pc = dt * self.SPEED
            self.y1 += pc
            self.y2 += pc
            if self.y2 >= 600:
                self.forward = False
                self.y1 = 600 - self.LENGTH
                self.y2 = 600
        else:
            pc = dt * self.SPEED
            self.y1 -= pc
            self.y2 -= pc
            if self.y1 <= 0:
                self.forward = True
                self.y1 = 0
                self.y2 = self.LENGTH
        
