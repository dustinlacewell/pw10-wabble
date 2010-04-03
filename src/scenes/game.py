import math, random, gc

import pyglet
from pyglet.window.key import *

from src.util import img, spr
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
        self.slime_group = pyglet.graphics.OrderedGroup(2)
        self.print_group = pyglet.graphics.OrderedGroup(1)
        self.bg_group = pyglet.graphics.OrderedGroup(0)
        # Manages the background effects
        self.bg = BackgroundManager(batch=self.batch, group=self.bg_group)
        
        # The collision machinery        
        self.coll_funcs = CollisionDispatcher()
        # Each entity pair has an algorithm
        self.coll_funcs.add(HorizontalLine, Player, coll_player_horizontal_line)
        self.coll_funcs.add(VerticalLine, Player, coll_player_vertical_line)
        self.coll_funcs.add(Blobule, Player, coll_blob_player)
        
        # The player blob
        self.blob_group = src.glsl.blob.BlobGroup(300, 300, 8, (0.125, 0.375, 0.0))
        self.blobule_group = src.glsl.blob.BlobGroup(0, 0, 8, (0.5, 0.0, 0.5))
        self.player = Player(self, self.blob_group, self.slime_group, self.batch)
        
        logo = spr('logo.png', batch = self.batch, group=self.scoregroup_hi)
        logo.image.anchor_x, logo.image.anchor_y = 300, logo.image.height / 2
        logo.x, logo.y = 300, 300
        self.logo = logo
        self.logo_fade = False
        
        self.load_sounds()
        
        # The blobule powerup
        self.blobule = Blobule(self.blobule_group)
        
        # The lasers
        self.lines = {}
        self.do_horiz = True
        pyglet.graphics.glLineWidth(3)
        
        # Score labels
        self.score = 0
        self.scores = []
        

    def enter(self):
        self.reset_blobule()
        if not self.window.music_player.playing:
            if __debug__: print 'starting playing game scene music'
            self.window.music_player.play()
        gc.disable()
        if __debug__: print "gc disabled"
    
    def leave(self):
        if __debug__: print "gc enabled"
        gc.enable()
    
    def load_sounds(self):
        self.scream1 = pyglet.media.load('dat/audio/fx/scream1.mp3', streaming=False)
        self.scream2 = pyglet.media.load('dat/audio/fx/scream2.mp3', streaming=False)
        self.scream3 = pyglet.media.load('dat/audio/fx/scream3.mp3', streaming=False)
        self.eat = pyglet.media.load('dat/audio/fx/fx3.mp3', streaming=False)
        
    def reset_blobule(self):
        '''give the blobule a random position'''
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
        elif t=='h' and abs(pos[1] - player_y) <= 32:
            self.add_line(r+1)
        elif t=='v' and abs(pos[1] - player_x) <= 32:
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
        
    def on_key_press(self, symbol, modifiers):
        if not self.logo_fade and self.logo.opacity == 255:
            self.logo_fade = True

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
                if self.player.remove_dot():
                    self.scream3.play()
                    self.window.scorescene(score=self.score)
                else:
                    random.choice((self.scream1, self.scream2)).play()
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
            if __debug__:
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
                
        if self.logo_fade and self.logo.opacity > 0:
            self.logo.opacity -= 75 * dt
            if self.logo.opacity <= 0:
                self.logo.opacity = 0
                self.logo_fade = False
            
    def draw(self):   
        self.batch.draw()
        self.blobule_group.draw(600, 600)
        self.blob_group.draw(600, 600)
        self.laser_batch.draw()
    
def coll_blob_player(b, player):
    dx = b.blob_group.x - player.blob.x
    dy = b.blob_group.y - player.blob.y
    if dx * dx + dy * dy < 20 * 20:
        return True
        for n in range(ndots):
            for blub in b.dots:
                dist_sq = ((blub.x - dot.x)**2) + ((blub.y - dot.y)**2)
                if dist_sq <= 5*5:
                    return True
    return False
    
def coll_player_vertical_line(line, player):
    dx = player.blob.x - line.x1
    if -15 < dx < 15:
        if player.blob.y - line.y2 <= 20 and line.y1 - player.blob.y <= 20:
            radius = 6
            if player.blob.y <= line.y2 and player.blob.y >= line.y1:
                # in the segment
                print 'expensive!'
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
                radius_sq = radius ** 2
                print 'expensive!'
                for dot in player.dots:
                    if (dot.x - line.x1) ** 2 + (dot.y - line_y) ** 2 < radius_sq:
                        if __debug__: print "vert out of segment collision, up of line:", line_y==line.y2
                        return True
    return False

def coll_player_horizontal_line(line, player):
    dy = player.blob.y - line.y1
    if -15 < dy < 15:
        if player.blob.x - line.x2 <= 20 and line.x1 - player.blob.x <= 20:
            radius = 6
            if player.blob.x <= line.x2 and player.blob.x >= line.x1:
                # in the segment
                print 'expensive!'
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
                radius_sq = radius ** 2
                print 'expensive!'
                for dot in player.dots:
                    if (dot.y - line.y1) ** 2 + (dot.x - line_x) ** 2 < radius_sq:
                        if __debug__: print "vert out of segment collision, left of line:", line_x==line.x1
                        return True
    return False

