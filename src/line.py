import math

import pyglet

from src.util import gradient

class Line(object):
    
    LENGTH = 30
    SPEED = 150
    HEATUP_RADIUS = 300
    
    gradient = gradient((1.0, 0.0, 0.0), (0.0, 0.0, 0.0), HEATUP_RADIUS)
    laser_fx = pyglet.media.load('dat/audio/fx/laser.mp3', streaming=False)

    def __init__(self, scene, batch, group, x1, y1, x2, y2):
        # TODO: add asserts
        assert(x1 <= x2)
        assert(y1 <= y2)
        
        self.scene = scene
        self.batch = batch
        
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.v1 = x2 - x1
        self.v2 = y2 - y1
        self.length_sq = float(self.v1 * self.v1 + self.v2 * self.v2)
        self.color = (255, 0, 0)
        self.vlist = batch.add(2, pyglet.gl.GL_LINES, group,
            ('v2f', (x1, y1, x2, y2)),
            ('c3f', (0, 0, 0, 0, 0, 0),
        ))
        self.play_fx()
        
        
    def update_vlist(self):
        self.update_color()
        # self.vlist.vertices = [self.x1, self.y1, self.x2, self.y2]
        verts = self.vlist.vertices
        verts[0] = self.x1
        verts[1] = self.y1
        verts[2] = self.x2
        verts[3] = self.y2
        self.vlist.colors = self.color*2
        
    def update_color(self):
        if self.scene.score >= 20:
            (player_x, player_y) = self.scene.player.get_position()
            dist = math.sqrt(((self.x1 - player_x)**2) + ((self.y1 - player_y)**2))
            dist = int(min(self.HEATUP_RADIUS - 1, dist))
            self.color = self.gradient[dist]
        
    def delete(self):
        self.vlist.delete()
        
    def play_fx(self):
        player = pyglet.media.Player()
        player.queue(self.laser_fx)
        player.volume = 0.15
        player.play()
        
        
class HorizontalLine(Line):
    def __init__(self, scene, batch, group, y_pos):
        x1 = 0
        x2 = self.LENGTH
        y1 = y2 = y_pos
        super(HorizontalLine, self).__init__(scene, batch, group, x1, y1, x2, y2)
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
                self.play_fx()
        else:
            pc = dt * self.SPEED
            self.x1 -= pc
            self.x2 -= pc
            if self.x1 <= 0:
                self.forward = True
                self.x1 = 0
                self.x2 = self.LENGTH
                self.play_fx()
        self.update_vlist()
                
class VerticalLine(Line):
    def __init__(self, scene, batch, group, x_pos):
        y1 = 0
        y2 = self.LENGTH
        x1 = x2 = x_pos
        super(VerticalLine, self).__init__(scene, batch, group, x1, y1, x2, y2)
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
                self.play_fx()
        else:
            pc = dt * self.SPEED
            self.y1 -= pc
            self.y2 -= pc
            if self.y1 <= 0:
                self.forward = True
                self.y1 = 0
                self.y2 = self.LENGTH
                self.play_fx()
        self.update_vlist()
    
