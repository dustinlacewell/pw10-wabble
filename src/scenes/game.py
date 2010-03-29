import math, random

import pyglet
from pyglet.window.key import *

from src.util import img
from src.blob import Blob
from src.player import Player
from src.collisiondispatch import CollisionDispatcher
from src.line import Line, HorizontalLine, VerticalLine
from src.background import BackgroundManager

# This scene class is the object that the application class maintains
class GameScene(object):
    def __init__(self, window):
        # Store a reference to the application window
        self.window = window
        
        self.keys = window.keys
        
        self.sprite_patch = pyglet.graphics.Batch()
        
        self.bg = BackgroundManager(min_t=8, max_t=9)
        
        self.blob_group = pyglet.graphics.OrderedGroup(1)
        self.print_group = pyglet.graphics.OrderedGroup(0)
        
        self.powerup = Blob(dots=0, batch=self.sprite_patch, group=self.blob_group)
        self.reset_powerup()
        
        self.coll_funcs = CollisionDispatcher()
        # add collision functions
        self.coll_funcs.add(HorizontalLine, Player, coll_segment_player)
        self.coll_funcs.add(VerticalLine, Player, coll_segment_player)
        self.coll_funcs.add(Blob, Player, coll_blob_player)
        
        # entities
        self.player = Player(self, batch=self.sprite_patch, group=self.blob_group, pgroup=self.print_group)
        self.lines = {}
        pyglet.graphics.glLineWidth(3)
        
    def on_mouse_motion(self, x, y, dx, dy):
        self.player.x = x
        self.player.y = y
        
    def reset_powerup(self):
        self.powerup.x = random.randint(30, 570)
        self.powerup.y = random.randint(30, 570)

    def update(self, dt):
        self.bg.update(dt)
        
        deleted_lines = []
        self.player.update(dt)
        
        for key, line in self.lines.iteritems():
            line.update(dt)
            check = False
            if isinstance(line, VerticalLine) and abs(line.slot - self.player.x) < 16:
                check = True
            elif isinstance(line, HorizontalLine) and abs(line.slot - self.player.y) < 16:
                check = True
                
            if check and self.coll_funcs.collide(line, self.player):
                deleted_lines.append(key)
                if self.player.remove_dot():
                    self.window.splashscene()

        for line in deleted_lines:
            del self.lines[line]
            
        if self.coll_funcs.collide(self.powerup, self.player):
            self.reset_powerup()
            self.player.add_dot()
            self.add_line()
        
    def add_line(self, r=0):
        if r == 500:
            return
        t = 'h' if random.randint(0, 1) else 'v'
        pos = (t, random.randint(0, 600))
        if pos in self.lines:
            self.add_line(r+1)
        else:
            if t == 'h':
                newline = HorizontalLine(self, None, pos[1])
            else:
                newline = VerticalLine(self, None, pos[1])
            self.lines[pos] = newline

    def draw(self):        
        self.bg.draw()
        self.sprite_patch.draw()
        
        for line in self.lines.itervalues():
            line.draw()
        
# the collision detection is not perfect
# should it detect collision for each Blob sepeartly?
        
def coll_line_player(line, player):
    w1 = player.x - line.x1 # vector from p1 to the player
    w2 = player.y - line.y1
    # print "w", w1, w2, line.v1, line.v2
    az = line.v1 * w2 - line.v2 * w1 # cross product
    a_squared = az * az
    dist_squared = a_squared / line.length_sq
    if player.radius * player.radius > dist_squared:
        print "line collision "
        return True
    return False

def coll_segment_player(seg, player):
    w1 = player.x - seg.x1 # vector from p1 to the player
    w2 = player.y - seg.y1
    u1 = seg.v1 / seg.LENGTH
    u2 = seg.v2 / seg.LENGTH
    s = w1 * u1 + w2 * u2
    
    prad_sq = player.radius * player.radius
    if s < 0:
        x = player.x - seg.x1
        y = player.y - seg.y1
        dist_sq = x * x + y * y
        # print "seg1", dist_sq, prad_sq
        if dist_sq < prad_sq:
            print "collision 1"
            return True
        return False
    elif s*s > seg.length_sq:
        x = player.x - seg.x2
        y = player.y - seg.y2
        dist_sq = x * x + y * y
        # print "seg2", dist_sq, prad_sq
        if dist_sq < prad_sq:
            print "collision 2"
            return True
        return False
    # print "line"
    return coll_line_player(seg, player)
    
    
    
def coll_blob_player(b, player):
    for dot in player.dots:
        dist = math.sqrt(((b.x - dot.x)**2) + ((b.y - dot.y)**2))
        if dist <= 16:
            return True
    return False