import math, random, gc

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
from scene import Scene

# This scene class is the object that the application class maintains
class GameScene(Scene):
    def __init__(self, window):
        # Store a reference to the application window
        self.window = window
        # Key handler shortcut
        self.keys = window.keys
        # The rendering batch
        self.batch = pyglet.graphics.Batch()
        self.laser_batch = pyglet.graphics.Batch()
        # The foreground rendering groups
        self.scoregroup_hi = pyglet.graphics.OrderedGroup(5)
        self.scoregroup_lo = pyglet.graphics.OrderedGroup(4)
        #self.laser_group = pyglet.graphics.OrderedGroup(3)
        #self.blob_group = pyglet.graphics.OrderedGroup(2)
        self.print_group = pyglet.graphics.OrderedGroup(1)
        self.bg_group = pyglet.graphics.OrderedGroup(0)
        # The containers for all blobs to be rendered
        
        # Manages the background effects
        self.bg = BackgroundManager(batch=self.batch, group=self.bg_group)
        # The collision machinery        
        self.coll_funcs = CollisionDispatcher()
        # Each entity pair has an algorithm
        # self.coll_funcs.add(HorizontalLine, Player, coll_segment_player)
        self.coll_funcs.add(HorizontalLine, Player, coll_player_horizontal_line)
        # self.coll_funcs.add(VerticalLine, Player, coll_segment_player)
        self.coll_funcs.add(VerticalLine, Player, coll_player_vertical_line)
        self.coll_funcs.add(Blobule, Player, coll_blob_player)
        # The player blob
        self.blob_group = src.glsl.blob.BlobGroup(300, 300, 8, (0.125, 0.375, 0.0))
        self.blobule_group = src.glsl.blob.BlobGroup(0, 0, 8, (0.5, 0.0, 0.5))
        self.player = Player(self, self.blob_group)
        #self.player = Player(self, batch=self.batch, group=self.blob_group, pgroup=self.print_group)
        #self.player.set_position(300, 500)
        self.score = 0
        self.load_sounds()
        # The blobule powerup
        self.blobule = Blobule(self.blobule_group)
        #self.blobule = Blob(dots=0, batch=self.batch, group=self.blob_group)
        #self.blobule.set_position(300, 300)
        # The lasers
        self.lines = {}
        self.do_horiz = True
        pyglet.graphics.glLineWidth(3)
        # Score labels
        self.scores = []
        
        gc.disable()

    def enter(self):
        self.reset_blobule()
        if not self.window.music_player.playing:
            if __debug__: print 'starting playing game scene music'
            self.window.music_player.play()
    
    def load_sounds(self):
        self.scream1 = pyglet.media.load('dat/audio/fx/scream1.mp3', streaming=False)
        self.scream2 = pyglet.media.load('dat/audio/fx/scream2.mp3', streaming=False)
        self.scream3 = pyglet.media.load('dat/audio/fx/scream3.mp3', streaming=False)
        self.eat = pyglet.media.load('dat/audio/fx/fx3.mp3', streaming=False)
        # self.blobule_appear = pyglet.media.load('dat/audio/fx/fx1.mp3', streaming=False)
        
    #===========================================================================
    # def remove_blobule(self):
    #    self.blobule_group.setPosition(-100, -100) # out of visible/reachable range
    #    pyglet.clock.schedule_once(self.reset_blobule, random.randrange(1,4))
    #===========================================================================
        
    def reset_blobule(self):
        '''give the blobule a random position'''
        # self.blobule_appear.play()
        self.blobule_group.setPosition(random.randint(30, 570), random.randint(30, 570))
        
    def add_line(self, r=0):
        '''add a new random line hazard'''
        if r == 500:
            return
        t = 'h' if self.do_horiz else 'v'
        pos = (t, random.randint(0, 600))
        (player_x, player_y) = self.player.get_position()
        if pos in self.lines:
            self.add_line(r+1)
        elif t=='h' and abs(pos[1] - player_y) <= 16:
            self.add_line(r+1)
        elif t=='v' and abs(pos[1] - player_x) <= 16:
            self.add_line(r+1)
        else:
            if t == 'h':
                newline = HorizontalLine(self, self.laser_batch, None, pos[1])
            else:
                newline = VerticalLine(self, self.laser_batch, None, pos[1])
            self.lines[pos] = newline
            self.do_horiz = not self.do_horiz
            
    def add_score(self):
        self.score += 1
        (blobule_x, blobule_y) = self.blobule.get_position()
        newscore = ScoreLabel(str(self.score), 
                  blobule_x, blobule_y, 
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

            if self.coll_funcs.collide(line, self.player):
                deleted_lines.append(key)
                n_times_before_die = 2
                if len(self.player.dots) <= 5 + (n_times_before_die + 1) * 3: # 3 dots are removed at once when hit by laser
                    # painfull screams
                    scream = random.choice([self.scream1, self.scream2])
                else:
                    scream = self.scream3
                scream.play()
                #remove_dot returns whether player is dead
                if self.player.remove_dot():
                    gc.enable()
                    self.window.scorescene(score=self.score)
        # clean up the dead lines
        for key in deleted_lines:
            line = self.lines.pop(key)
            line.delete()
        # Player-Blobule collision
        if self.coll_funcs.collide(self.blobule, self.player):
            self.eat.play()
            self.add_score()
            self.reset_blobule() # new blobule position
            player_pos = self.player.get_position()
            self.player.add_dot(*player_pos) # increase bodymass
            self.add_line() # new random hazard
            print "lines", len(self.lines)
            
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
        self.laser_batch.draw()
        
        
        

    
def coll_blob_player(b, player):
    dx = b.blob_group.x - player.blob.x
    dy = b.blob_group.y - player.blob.y
    if dx * dx + dy * dy < 30 * 30:
        for dot in player.dots:
            for blub in b.dots:
                dist_sq = ((blub.x - dot.x)**2) + ((blub.y - dot.y)**2)
                if dist_sq <= 5*5:
                    return True
    return False
    
def coll_player_vertical_line(line, player):
    dx = player.blob.x - line.x1
    if -15 < dx < 15:
        if player.blob.y - line.y2 <= 20:
            if line.y1 - player.blob.y <= 20:
                radius = 6
                if player.blob.y <= line.y2 and player.blob.y >= line.y1:
                    # in the segment
                    for dot in player.dots:
                        dx = line.x1 - dot.x
                        if -radius <= dx <= radius:
                            if __debug__: print "vert in segment collision"
                            return True
                else:
                    if player.blob.y > line.y2:
                        line_y = line.y2
                    else:
                        line_y = line.y1
                    radius_sq = radius * radius
                    for dot in player.dots:
                        if (dot.x - line.x1) ** 2 + (dot.y - line_y) ** 2 < radius_sq:
                            if __debug__: print "vert out of segment collision, up of line:", line_y==line.y2
                            return True
    return False

def coll_player_horizontal_line(line, player):
    dy = player.blob.y - line.y1
    if -15 < dy < 15:
        if player.blob.x - line.x2 <= 20:
            if line.x1 - player.blob.x <= 20:
                radius = 6
                if player.blob.x <= line.x2 and player.blob.x >= line.x1:
                    # in the segment
                    for dot in player.dots:
                        dy = line.y1 - dot.y
                        if -radius <= dy <= radius:
                            if __debug__: print "vert in segment collision"
                            return True
                else:
                    if player.blob.x > line.x2:
                        line_x = line.x2
                    else:
                        line_x = line.x1
                    radius_sq = radius * radius
                    for dot in player.dots:
                        if (dot.y - line.y1) ** 2 + (dot.x - line_x) ** 2 < radius_sq:
                            if __debug__: print "vert out of segment collision, left of line:", line_x==line.x1
                            return True
    return False

# def coll_line_player(line, player):
    # for dot in player.dots:
        # w1 = dot.x - line.x1 # vector from p1 to the player
        # w2 = dot.y - line.y1
        # #print "w", w1, w2, line.v1, line.v2
        # az = line.v1 * w2 - line.v2 * w1 # cross product
        # a_squared = az * az
        # dist_squared = a_squared / line.length_sq
        # if player.radius * player.radius > dist_squared:
            # print "line collision "
            # return True
    # return False

# def coll_segment_player(seg, player):
    # for dot in player.dots:
        # w1 = dot.x - seg.x1 # vector from p1 to the player
        # w2 = dot.y - seg.y1
        # u1 = seg.v1 / seg.LENGTH
        # u2 = seg.v2 / seg.LENGTH
        # s = w1 * u1 + w2 * u2
        
        # prad_sq = dot.radius * dot.radius
        # if s < 0:
            # x = dot.x - seg.x1
            # y = dot.y - seg.y1
            # dist_sq = x * x + y * y
            # #print "seg1", dist_sq, prad_sq
            # if dist_sq < prad_sq:
                # print "collision 1"
                # return True
            # return False
        # elif s*s > seg.length_sq:
            # x = dot.x - seg.x2
            # y = dot.y - seg.y2
            # dist_sq = x * x + y * y
            # #print "seg2", dist_sq, prad_sq
            # if dist_sq < prad_sq:
                # print "collision 2"
                # return True
            # return False
    # return False    
    
