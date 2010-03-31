import pyglet
from pyglet.window.key import *
import random

from src.blob import Blob

import src.glsl.blob

class Player(Blob):
    
    base_dot_acceleration = 0.2
    
    radius = 16
    #def __init__(self, scene, batch=None, group=None, pgroup=None):
    def __init__(self, scene, group, x, y):
        #super(Player, self).__init__(dots=5, doprints=True, batch=batch, group=group, pgroup=pgroup)
        super(Player, self).__init__(group)
        self.scene = scene
        self.speed = self.MAXSPEED
        self.x = x
        self.y = y
        
        self.blob = src.glsl.blob.Blob(
         x, y, acceleration_cap=0.1,
         radius=8.0, sides=12,
         r=random.uniform(0.1, 0.35),
         g=random.uniform(0.1, 0.35),
         b=random.uniform(0.0, 0.075)
         #r=1.0, g=1.0, b=0.0
        )
        self.dots.append(self.blob)
        group.addBlob(self.blob)
        
        for n in xrange(5):
            self.add_dot(x, y)
            
    def get_blob(self):
        return self.blob
        
    def handle_movement(self, dt):
        k = self.scene.keys
        #old = self.position
        old_x = self.x
        old_y = self.y
        rawspeed = self.MAXSPEED - ((len(self.dots) - 5) * 10)
        speed = max(self.MINSPEED, rawspeed) * dt
        
        self.y += speed if k[UP] else -speed if k[DOWN] else 0
        self.x += speed if k[RIGHT] else -speed if k[LEFT] else 0
        
        return (self.x - old_x, self.y - old_y)
        """if old != self.position:
            self.wobble(dt)"""
        
    def update(self, dt):
        (offset_x, offset_y) = self.handle_movement(dt)
        
        location = (self.x, self.y)
        for dot in self.dots:
            dot.setRoot(*location)
            if offset_x or offset_y:
                dot.x += offset_x
                dot.y += offset_y
                dot.acceleration_cap = self.base_dot_acceleration * 6.5
            else:
                dot.acceleration_cap -= dot.acceleration_cap * .33
                if dot.acceleration_cap <= .03:
                    dot.acceleration_cap = 0
        (self.blob.x, self.blob.y) = location
        
    def remove_dot(self):
        super(Player, self).remove_dot()
        super(Player, self).remove_dot()
        super(Player, self).remove_dot()
        if len(self.dots) <= 5:
            return True
