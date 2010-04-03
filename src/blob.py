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
        self.dots = group.blobs
        
    def _update_wander_limit(self):
        dot_distance = math.sqrt((len(self.dots) - 1) * math.pi)
        for dot in self.dots[1:]:
            dot.wander_limit = dot_distance
            
    def add_dot(self, x, y, accel_min=0.025, accel_max=1.0):
        if len(self.dots) < self.MAXDOTS:
            self.dots.append(src.glsl.blob.Blob(
             x, y,
             acceleration_max=accel_max, acceleration_min=accel_min
            ))
        self._update_wander_limit()
        
    def remove_dot(self):
        if len(self.dots) > 1:
            old_dot = self.dots.pop(1)
            self._update_wander_limit()
            return True
        return False
        
    def get_position(self):
        return (self.blob_group.x, self.blob_group.y)
        
class Blobule(Blob):
    def __init__(self, group, doprints=True, dots=10, accel_min=0.0375, accel_max=1.5):
        super(Blobule, self).__init__(group)
        blobule = src.glsl.blob.Blob(
         group.x, group.y,
         0.0, 0.2,
         radius=group.core_radius, sides=12,
        )
        group.addBlob(blobule)
        
        for i in xrange(dots):
            self.add_dot(group.x, group.y, accel_min=accel_min, accel_max=accel_max)
            
