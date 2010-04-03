import pyglet
from pyglet.window.key import *
import random

from src.blob import Blob
import src.util

import src.glsl.blob

class Player(Blob):
    slime_images = None
    slime_timeout = 0.0
    
    def __init__(self, scene, group, slime_group, slime_batch):
        super(Player, self).__init__(group)
        self.scene = scene
        self.speed = self.MAXSPEED
        
        if not self.slime_images:
            self.slime_images = (
             src.util.img('slime_1.png'),
             src.util.img('slime_2.png'),
             src.util.img('blob3.png'),
            )
            for image in self.slime_images:
                image.anchor_x = image.width // 2
                image.anchor_y = image.height // 2
        self.slime_trail = []
        self.slime_group = slime_group
        self.slime_batch = slime_batch
        
        self.blob = src.glsl.blob.Blob(
         group.x, group.y,
         radius=group.core_radius, sides=12,
        )
        group.addBlob(self.blob)
        
        self.radius = self.blob.radius
        
        #for n in xrange(5):
        #    self.add_dot(group.x, group.y)
        self.add_dot(group.x, group.y)    
    def get_blob(self):
        return self.blob
        
    def handle_movement(self, dt):
        k = self.scene.keys
        
        old_x = new_x = self.blob_group.x
        old_y = new_y = self.blob_group.y
        #rawspeed = self.MAXSPEED - ((len(self.dots) - 5) * 10)
        #speed = max(self.MINSPEED, rawspeed) * dt
        speed = int(
         (
          self.MINSPEED + ( (self.MAXSPEED - self.MINSPEED) * (1.0 - (len(self.dots) / float(self.MAXDOTS)) ** 1)
          )
         ) * dt
        )
        
        dir_y = 1 if k[UP] else -1 if k[DOWN] else 0
        dir_x = 1 if k[RIGHT] else -1 if k[LEFT] else 0
        
        new_length = (dir_x * dir_x + dir_y * dir_y) ** 0.5
        
        if new_length != 0:
            new_x += dir_x / new_length * speed
            new_y += dir_y / new_length * speed
        
        
        return (new_x - old_x, new_y - old_y)
        
    def update(self, dt):
        (offset_x, offset_y) = self.handle_movement(dt)
        self.slime_timeout = max(0.0, self.slime_timeout - dt)
        
        #Clean up slime trail.
        dead_slime = []
        dot_count = len(self.dots)
        fade_rate = 0.75 - (dot_count / 175.0) * (1.0 + dt)
        for slime in self.slime_trail:
            slime.opacity = int(slime.opacity * slime.orate)
            if slime.opacity <= 0.05:
                dead_slime.append(slime)
            else:
                slime.scale *= slime.srate
        for slime in dead_slime:
            slime.delete()
            self.slime_trail.remove(slime)
            
        if offset_x or offset_y:
            #Prevent the blob from leaving the field.
            if offset_x + self.blob_group.x > 600:
                offset_x = 600 - self.blob_group.x
            elif offset_x + self.blob_group.x < 0:
                offset_x = -self.blob_group.x
            if offset_y + self.blob_group.y > 600:
                offset_y = 600 - self.blob_group.y
            elif offset_y + self.blob_group.y < 0:
                offset_y = -self.blob_group.y
                
            if offset_x or offset_y:
                if self.slime_timeout == 0.0:
                    self.slime_timeout = 0.06 + dot_count / 150.0
                    #Add to slime trail.
                    for dot in self.dots:
                        slime = pyglet.sprite.Sprite(
                         random.choice(self.slime_images),
                         x=dot.x, y=dot.y,
                         batch=self.slime_batch, group=self.slime_group
                        )
                        slime.scale = 0.85
                        slime.rotation = random.randint(0, 360)
                        slime.srate = random.uniform(0.975, 0.99)
                        slime.orate = random.uniform(0.8, 0.9)
                        self.slime_trail.append(slime)
                        
                #Update the blob's position.
                self.blob_group.offsetPosition(offset_x, offset_y)
                
    def remove_dot(self):
        return super(Player, self).remove_dot() or super(Player, self).remove_dot() or super(Player, self).remove_dot()
        #if len(self.dots) <= 5:
        #    return True
        
