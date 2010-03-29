import random, math

import pyglet

from src.util import img, spr

class Dot(pyglet.sprite.Sprite):
    
    dryrate = 0.01
    
    def __init__(self, blob, max_off=3, footprints=True, batch=None, group=None, pgroup=None):
        super(Dot, self).__init__(blob.image, batch=batch, group=group)
        self.max_off = max_off
        self.blob = blob
        
        self.sprbatch = batch
        self.pgroup = pgroup
        
        self.scale = .75
        
        self.doprints = footprints
        self.footprints = []
        self.oldpos = blob.position
        self.dryspeed = random.randint(40, 60)
        if self.doprints:
            pyglet.clock.schedule_interval(self.dry_footprints, self.dryrate)
            pyglet.clock.schedule_interval(self.step, min(0.25, random.random() + 0.05))
        
        self.wobble(0)
        
    def dry_footprints(self, dt):
        delta = self.dryspeed * dt
        for fp in list(self.footprints):
            fp.opacity -= delta
            if fp.opacity <= 0:
                self.footprints.remove(fp)
                
    def step(self, dt):
        if self.oldpos != self.blob.position:
            newprint = pyglet.sprite.Sprite(self.image, batch=self.sprbatch, group=self.pgroup)
            newprint.position = self.position
            newprint.opacity = 128
            newprint.scale = .75
            self.footprints.append(newprint)
        
    def wobble(self, dots):
        ddots = int(dots * 0.7)
        radius = random.randint(0, ddots)
        angle = random.randint(0, 360)
        xoff = self.blob.x + radius*math.cos(angle)
        yoff = self.blob.y + radius*math.sin(angle)
        #=======================================================================
        # xoff = min(10, random.randint(-ddots, ddots))
        # yoff = min(10, random.randint(-ddots, ddots))
        #=======================================================================
        self.set_position(xoff, yoff)
                
class Blob(pyglet.sprite.Sprite):
    
    MAXDOTS = 10
    
    blob_sprites = [
    
    'blob.png', 'blob2.png', 'blob3.png'
                    
    ]
    
    fastwobble = 0.05
    
    def __init__(self, dots=10, wobblerate=.15, footprints=True, batch=None, group=None, pgroup=None):
        super(Blob, self).__init__(img(random.choice(self.blob_sprites)), batch=batch, group=group)
        
        self.image.anchor_x = 8
        self.image.anchor_y = 8
        
        self.fastwobble_t = 0.0
        
        self.pgroup = pgroup
        
        self.footprints = footprints
        
        self.dots = []
        for n in xrange(dots):
            self.dots.append(Dot(self, footprints=footprints, batch=batch, group=group, pgroup=pgroup))
        
        pyglet.clock.schedule_interval(self.wobble, wobblerate)
        
    def wobble(self, dt):
        self.fastwobble_t += dt
        if self.fastwobble_t >= self.fastwobble:
            for dot in self.dots:
                dot.wobble(len(self.dots))
            self.fastwobble_t = 0.0
            
    def add_dot(self):
        if len(self.dots) < 20:
            self.dots.append(Dot(self, footprints=self.footprints, batch=self.batch, group=self.group, pgroup=self.pgroup))
            
    def remove_dot(self):
        d = self.dots.pop()