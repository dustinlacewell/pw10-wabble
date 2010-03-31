import random, math
#from collections import deque
from random import uniform

import pyglet

from src.util import img, spr

import src.glsl.blob

"""class Dot(pyglet.sprite.Sprite):
    
    MAXOFFSET = 3
    radius = 10
    dryrate = 0.1
    
    def __init__(self, blob, batch=None, group=None):
        super(Dot, self).__init__(blob.image, batch=batch, group=group)
        self.blob = blob
        self.scale = .8
        self.wobble(0)
        
    def wobble(self, dots):
        ddots = int(dots * 0.7)
        radius = random.randint(0, ddots)
        angle = random.randint(0, 360)
        xoff = self.blob.x + radius*math.cos(angle)
        yoff = self.blob.y + radius*math.sin(angle)
        self.set_position(xoff, yoff)"""
                
class Blob(object):
    
    MAXSPEED = 150
    MINSPEED = 50
    MAXDOTS = 25
    """MAXPRINTS = 25
    IDLEWOBBLE = 0.15
    FASTWOBBLE = 0.05
    DRYTIME = 0.01"""
    
    #blob_sprites = [  
    #'blob.png', 'blob2.png', 'blob3.png'
    #]
    #radius = 8
    def __init__(self, group, doprints=True):
        self.blob_group = group
        
        #self.image.anchor_x = 8
        #self.image.anchor_y = 8
        
        #self.wobble_t = 0.0
        
        #self.batch = batch
        #self.group = group
        #self.pgroup = pgroup
        
        #self.oldposition = self.position

        self.dots = []
        
        """self.prints = list()
        self.doprints = doprints
        
        if self.doprints:
            for n in xrange(prints):
                newprint = spr(random.choice(self.blob_sprites), batch=self.batch, group=self.pgroup)
                newprint.scale = .75
                newprint.opacity = 0
                newprint.image.anchor_x, newprint.image.anchor_y = self.image.anchor_x, self.image.anchor_y
                self.prints.append(newprint)
        
            
        
        pyglet.clock.schedule_interval(self.wobble, self.IDLEWOBBLE)
        if self.doprints:
            pyglet.clock.schedule_once(self.footprint, random.random())
            pyglet.clock.schedule_interval(self.dry, self.DRYTIME)"""
        
    """def wobble(self, dt):
        self.wobble_t += dt
        if self.wobble_t >= self.FASTWOBBLE:
            for dot in self.dots:
                dot.wobble(len(self.dots))
            self.wobble_t = 0.0"""
            
    def update_wander_limit(self):
        dot_distance = math.sqrt((len(self.dots) - 1) * 3)
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
        
    """def footprint(self, dt):
        if self.oldposition != self.position:
            self.oldposition = self.position
            for p in self.prints:
                if p.opacity == 0:
                    p.opacity = 100
                    p.position = random.choice(self.dots).position if self.dots else self.position
                    break
        pyglet.clock.schedule_once(self.footprint, min(0.01, random.random()))
        
    def dry(self, dt):
        for p in list(self.prints):
            p.opacity = max(0, p.opacity - (random.random() * 300) * dt)"""
            
class Blobule(Blob):
    x = 300
    y = 300
    
    def __init__(self, group, doprints=True):
        super(Blobule, self).__init__(group, doprints=doprints)
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
            
