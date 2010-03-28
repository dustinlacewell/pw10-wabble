import random

import pyglet

from src.util import img

class Dot(pyglet.sprite.Sprite):
    def __init__(self, blob, max_off=3, batch=None):
        super(Dot, self).__init__(blob.image, batch=batch)
        self.max_off = max_off
        self.blob = blob
        self.wobble()
        
    def wobble(self):
        xoff = random.randint(-self.max_off, self.max_off)
        yoff = random.randint(-self.max_off, self.max_off)
        self.set_position(self.blob.x + xoff, self.blob.y + yoff)
        
        
class Blob(pyglet.sprite.Sprite):
    def __init__(self, filename, dots=10, wobblerate=.1, batch=None):
        super(Blob, self).__init__(img(filename), batch=batch)
        self.dots = []
        for n in xrange(dots):
            self.dots.append(Dot(self, batch=batch))
        pyglet.clock.schedule_interval(self.wobble, wobblerate)
        
    def wobble(self, dt):
        for dot in self.dots:
            dot.wobble()
 