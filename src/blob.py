import random

import pyglet

from src.util import img, spr

class Dot(pyglet.sprite.Sprite):
    
    dryrate = 0.01
    
    def __init__(self, blob, max_off=3, batch=None, group=None, pgroup=None):
        super(Dot, self).__init__(blob.image, batch=batch, group=group)
        self.max_off = max_off
        self.blob = blob
        
        self.sprbatch = batch
        self.pgroup = pgroup
        
        self.footprints = []
        self.oldpos = blob.position
        pyglet.clock.schedule_interval(self.dry_footprints, self.dryrate)
        pyglet.clock.schedule_interval(self.step, min(0.65, random.random() + 0.25))
        
        self.wobble(0)
        
    def dry_footprints(self, dt):
        for fp in list(self.footprints):
            fp.opacity -= 80 * dt
            if fp.opacity <= 0:
                #pyglet.clock.unschedule(self.dry_footprints)
                #pyglet.clock.unschedule(self.step)
                fp.delete()
                self.footprints.remove(fp)
                
    def step(self, dt):
        if self.oldpos != self.blob.position:
            newprint = pyglet.sprite.Sprite(self.image, batch=self.sprbatch, group=self.pgroup)
            newprint.position = self.position
            newprint.opacity = 128
            self.footprints.append(newprint)
        
    def wobble(self, dots):
        xoff = random.randint(-dots, dots)
        yoff = random.randint(-dots, dots)
        self.set_position(self.blob.x + xoff, self.blob.y + yoff)
        

        
class Blob(pyglet.sprite.Sprite):
    
    blob_sprites = [
    
    'blob.png', 'blob2.png', 'blob3.png'
                    
    ]
    
    fastwobble = 0.05
    
    def __init__(self, dots=10, wobblerate=.15, batch=None, group=None, pgroup=None):
        super(Blob, self).__init__(img(random.choice(self.blob_sprites)), batch=batch, group=group)
        
        self.image.anchor_x = 8
        self.image.anchor_y = 8
        
        self.fastwobble_t = 0.0
        
        self.pgroup = pgroup
        
        self.dots = []
        for n in xrange(dots):
            self.dots.append(Dot(self, batch=batch, group=group, pgroup=pgroup))
        
        pyglet.clock.schedule_interval(self.wobble, wobblerate)
        
    def wobble(self, dt):
        self.fastwobble_t += dt
        if self.fastwobble_t >= self.fastwobble:
            for dot in self.dots:
                dot.wobble(len(self.dots))
            self.fastwobble_t = 0.0
 