import pyglet
from pyglet.window.key import *
import random

from src.blob import Blob

import src.glsl.blob

class Player(Blob):
    def __init__(self, scene, group):
        super(Player, self).__init__(group)
        self.scene = scene
        self.speed = self.MAXSPEED
        
        self.blob = src.glsl.blob.Blob(
         group.x, group.y,
         radius=group.core_radius, sides=12,
        )
        group.addBlob(self.blob)
        
        self.radius = self.blob.radius
        
        for n in xrange(5):
            self.add_dot(group.x, group.y)
            
    def get_blob(self):
        return self.blob
        
    def handle_movement(self, dt):
        k = self.scene.keys
        
        old_x = new_x = self.blob_group.x
        old_y = new_y = self.blob_group.y
        rawspeed = self.MAXSPEED - ((len(self.dots) - 5) * 10)
        speed = max(self.MINSPEED, rawspeed) * dt
        
        new_y += speed if k[UP] else -speed if k[DOWN] else 0
        new_x += speed if k[RIGHT] else -speed if k[LEFT] else 0
        
        return (new_x - old_x, new_y - old_y)
        
    def update(self, dt):
        (offset_x, offset_y) = self.handle_movement(dt)
        
        if offset_x + self.blob_group.x > 600:
            offset_x = 600 - self.blob_group.x
        elif offset_x + self.blob_group.x < 0:
            offset_x = -self.blob_group.x
        if offset_y + self.blob_group.y > 600:
            offset_y = 600 - self.blob_group.y
        elif offset_y + self.blob_group.y < 0:
            offset_y = -self.blob_group.y
        self.blob_group.offsetPosition(offset_x, offset_y)
        
    def remove_dot(self):
        super(Player, self).remove_dot()
        super(Player, self).remove_dot()
        super(Player, self).remove_dot()
        if len(self.dots) <= 5:
            return True
            
