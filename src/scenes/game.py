import math, random

import pyglet
from pyglet.window.key import *

from src.util import img
from src.blob import Blob, Blobule
from src.player import Player
from src.collisiondispatch import CollisionDispatcher
from src.line import Line, HorizontalLine, VerticalLine
from src.background import BackgroundManager
from src.score import ScoreLabel

import src.glsl.blob

# This scene class is the object that the application class maintains
class GameScene(object):
    def __init__(self, window):
        # Store a reference to the application window
        self.window = window
        # Key handler shortcut
        self.keys = window.keys
        # The rendering batch
        self.batch = pyglet.graphics.Batch()
        # The foreground rendering groups
        self.scoregroup_hi = pyglet.graphics.OrderedGroup(5)
        self.scoregroup_lo = pyglet.graphics.OrderedGroup(4)
        self.laser_group = pyglet.graphics.OrderedGroup(3)
        #self.blob_group = pyglet.graphics.OrderedGroup(2)
        self.print_group = pyglet.graphics.OrderedGroup(1)
        self.bg_group = pyglet.graphics.OrderedGroup(0)
        # The containers for all blobs to be rendered
        
        # Manages the background effects
        self.bg = BackgroundManager(batch=self.batch, group=self.bg_group)
        # The collision machinery        
        self.coll_funcs = CollisionDispatcher()
        # Each entity pair has an algorithm
        self.coll_funcs.add(HorizontalLine, Player, coll_segment_player)
        self.coll_funcs.add(VerticalLine, Player, coll_segment_player)
        self.coll_funcs.add(Blob, Player, coll_blob_player)
        # The player blob
        self.blob_group = src.glsl.blob.BlobGroup()
        self.blobule_group = src.glsl.blob.BlobGroup()
        self.player = Player(self, self.blob_group, 300, 300)
        #self.player = Player(self, batch=self.batch, group=self.blob_group, pgroup=self.print_group)
        #self.player.set_position(300, 500)
        self.score = 0
        # The blobule powerup
        self.blobule = Blobule(self.blobule_group)
        self.reset_blobule()
        #self.blobule = Blob(dots=0, batch=self.batch, group=self.blob_group)
        #self.blobule.set_position(300, 300)
        # The lasers
        self.lines = {}
        self.do_horiz = True
        pyglet.graphics.glLineWidth(3)
        # Score labels
        self.scores = []     
        
    def reset_blobule(self):
        '''give the blobule a random position'''
        self.blobule.set_position(random.randint(30, 570), random.randint(30, 570))
        
    def add_line(self, r=0):
        '''add a new random line hazard'''
        if r == 500:
            return
        t = 'h' if self.do_horiz else 'v'
        pos = (t, random.randint(0, 600))
        if pos in self.lines:
            self.add_line(r+1)
        elif t=='h' and abs(pos[1] - self.player.y) <= 16:
            self.add_line(r+1)
        elif t=='v' and abs(pos[1] - self.player.x) <= 16:
            self.add_line(r+1)
        else:
            if t == 'h':
                newline = HorizontalLine(self, self.batch, self.laser_group, pos[1])
            else:
                newline = VerticalLine(self, self.batch, self.laser_group, pos[1])
            self.lines[pos] = newline
            self.do_horiz = not self.do_horiz
            
    def add_score(self):
        self.score += 1
        newscore = ScoreLabel(str(self.score), 
                  self.blobule.x, self.blobule.y, 
                  color=(0, 255, 0), size=12, 
                  batch=self.batch, group=self.scoregroup_hi)
        self.scores.append(newscore)

    def on_mouse_motion(self, x, y, dx, dy):
        self.player.x = x
        self.player.y = y

    def update(self, dt):
        self.bg.update(dt) # background effects
        self.player.update(dt)
        self.blob_group.tick()
        self.blobule_group.tick()
        # Line-Player collision
        deleted_lines = []
        for key, line in self.lines.iteritems():
            line.update(dt)
            check = False # exclude impossible collisions
            if isinstance(line, VerticalLine) and abs(line.slot - self.player.x) < 16:
                check = True
            elif isinstance(line, HorizontalLine) and abs(line.slot - self.player.y) < 16:
                check = True
            if check and self.coll_funcs.collide(line, self.player):
                deleted_lines.append(key)
                # remove_dot returns whether player is dead
                if self.player.remove_dot():
                    self.window.splashscene()
        # clean up the dead lines
        for key in deleted_lines:
            line = self.lines.pop(key)
            line.delete()
        # Player-Blobule collision
        #self.coll_funcs.collide(self.blobule, self.player):
        if ((self.blobule.x - self.player.x) ** 2 + (self.blobule.y - self.player.y) ** 2) ** 0.5 <= 8.0:
            self.add_score()
            self.reset_blobule() # new blobule position
            self.player.add_dot(self.player.x, self.player.y, r=0.0, g=1.0, b=0.0) # increase bodymass
            self.add_line() # new random hazard
            
            if self.score >= 5:
                self.bg.do_fade = True
            if self.score >= 15:
                self.bg.do_zoom = True
            if self.score >= 25:
                self.bg.do_spin = True
            
        for label in list(self.scores):
            if label.update(dt):
                self.scores.remove(label)
                label.delete()
            
    def draw(self):   
        self.batch.draw()
        self.blobule_group.draw(600, 600)
        self.blob_group.draw(600, 600)
        
        
# the collision detection is not perfect
# should it detect collision for each Blob sepeartly?
        
def coll_line_player(line, player):
    for dot in player.dots:
        w1 = dot.x - line.x1 # vector from p1 to the player
        w2 = dot.y - line.y1
        # print "w", w1, w2, line.v1, line.v2
        az = line.v1 * w2 - line.v2 * w1 # cross product
        a_squared = az * az
        dist_squared = a_squared / line.length_sq
        if player.radius * player.radius > dist_squared:
            print "line collision "
            return True
    return False

def coll_segment_player(seg, player):
    for dot in player.dots:
        w1 = dot.x - seg.x1 # vector from p1 to the player
        w2 = dot.y - seg.y1
        u1 = seg.v1 / seg.LENGTH
        u2 = seg.v2 / seg.LENGTH
        s = w1 * u1 + w2 * u2
        
        prad_sq = dot.radius * dot.radius
        if s < 0:
            x = dot.x - seg.x1
            y = dot.y - seg.y1
            dist_sq = x * x + y * y
            # print "seg1", dist_sq, prad_sq
            if dist_sq < prad_sq:
                print "collision 1"
                return True
            return False
        elif s*s > seg.length_sq:
            x = dot.x - seg.x2
            y = dot.y - seg.y2
            dist_sq = x * x + y * y
            # print "seg2", dist_sq, prad_sq
            if dist_sq < prad_sq:
                print "collision 2"
                return True
            return False
    return False    
    
def coll_blob_player(b, player):
    for dot in player.dots:
        dist = math.sqrt(((b.x - dot.x)**2) + ((b.y - dot.y)**2))
        if dist <= 10:
            return True
    return False
