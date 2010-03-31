import random, math
#from collections import deque
from random import uniform

import pyglet

from src.util import img, spr

import src.glsl.blob
                
class Blob(object):
    
    MAXSPEED = 150
    MINSPEED = 50
    MAXDOTS = 25

    def __init__(self, group):
        self.blob_group = group
        self.dots = []
            
    def update_wander_limit(self):
        dot_distance = math.sqrt((len(self.dots) - 1) * 2)
        for dot in self.dots[1:]:
            dot.wander_limit = dot_distance
            
    def add_dot(self, x, y, r=None, g=None, b=None, cap=0.2):
        if len(self.dots) < self.MAXDOTS:
            if r is None:
                r = uniform(0.05, 0.125)
            if g is None:
                g = uniform(0.05, 0.25)
            if b is None:
                b = uniform(0.0, 0.075)
                
            new_dot = src.glsl.blob.Blob(
             x, y, acceleration_cap=cap,
             r=r, g=g, b=b
            )
            self.dots.append(new_dot)
            self.blob_group.addBlob(new_dot)
        self.update_wander_limit()
        
    def remove_dot(self):
        if len(self.dots) > 1:
            old_dot = self.dots.pop(1)
            self.blob_group.removeBlob(old_dot)
            self.update_wander_limit()
            return True
        return False

            
class Blobule(Blob):
    x = 300
    y = 300
    
    def __init__(self, group, doprints=True):
        super(Blobule, self).__init__(group)
        blobule = src.glsl.blob.Blob(
         self.x, self.y,
         0.0, 0.2,
         radius=8.0, sides=12,
         r=0.1, g=0.1, b=0.75
        )
        self.dots.append(blobule)
        group.addBlob(blobule)
        
        for i in xrange(10):
            self.add_dot(self.x, self.y, r=0.05, g=0.05, b=0.35)
            
    def set_position(self, x, y):
        for dot in self.dots:
            self.x = dot.x = dot.root_x = x
            self.y = dot.y = dot.root_y = y
            
