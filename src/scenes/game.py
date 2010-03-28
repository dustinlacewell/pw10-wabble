import math

import pyglet
from pyglet.window.key import *

from src.util import img
from src.blob import Blob
from src.player import Player
from src.collisiondispatch import CollisionDispatcher
from src.line import Line

# This scene class is the object that the application class maintains
class GameScene(object):
    def __init__(self, window):
        # Store a reference to the application window
        self.window = window
        
        self.keys = window.keys
        
        self.sprite_patch = pyglet.graphics.Batch()
        self.blob_group = pyglet.graphics.OrderedGroup(1)
        self.print_group = pyglet.graphics.OrderedGroup(0)
        
        self.powerup = Blob(dots=0, batch=self.sprite_patch, group=self.blob_group)
        self.reset_powerup()
        
        self.coll_funcs = CollisionDispatcher()
        # add collision functions
        self.coll_funcs.add(Line, Player, coll_line_player)
        self.coll_funcs.add(Blob, Player, coll_blob_player)
        
        # entities
        self.player = Player(self, batch=self.sprite_patch, group=self.blob_group, pgroup=self.print_group)
        self.lines = []
        
        # TODO: remove, just for testing
        self.lines.append(Line(0, 0, 100, 100))
        
    def on_key_press(self, symbol, modifiers):
        if symbol in [UP, DOWN, LEFT, RIGHT]:
            self.player.handle_movement(symbol)
        
    def on_mouse_motion(self, x, y, dx, dy):
        self.player.x = x
        self.player.y = y
        
    def reset_powerup(self):
        self.powerup.x = random.randint(30, 570)
        self.powerup.y = random.randint(30, 570)

    def update(self, dt):
        self.player.update(dt)
        for line in self.lines:
            if self.coll_funcs.collide(line, self.player):
                pass
            
        if self.coll_funcs.collide(self.powerup, self.player):
            self.reset_powerup()
        
        

    def draw(self):
        self.sprite_patch.draw()
        
        
def coll_line_player(line, player):
    w1 = player.x - line.x1 # vector from p1 to the player
    w2 = player.y - line.y1
    # print "w", w1, w2, line.v1, line.v2
    az = line.v1 * w2 - line.v2 * w1 # cross product
    a_squared = az * az
    dist_squared = a_squared / line.length_sq
    if player.radius * player.radius > dist_squared:
        return True
    return False

def coll_blob_player(b, player):
    for dot in player.dots:
        dist = math.sqrt(((b.x - dot.x)**2) + ((b.y - dot.y)**2))
        if dist <= 32:
            return True
    return False