import random
from collections import deque

import pyglet

from src.util import spr

class BackgroundManager(object):
    
    MAXOPACITY = 145
    FADEDELAY = .5
    FADEAMOUNT = 15
    
    ZOOMAMOUNT = 0.001
    
    def __init__(self, rotation='backgrounds.txt', min_t=60, max_t=120, rate=50):
        self.min_t = min_t
        self.max_t = max_t    
        self.rate = rate # fade rate    
            
        self.batch = pyglet.graphics.Batch()
        self.rotation = deque()
        for line in pyglet.resource.file(rotation):
            newspr = spr(line.strip(), batch=self.batch)
            newspr.image.anchor_x, newspr.image.anchor_y = 300, 300
            newspr.x, newspr.y = 300, 300
            newspr.visible = False
            self.rotation.append( newspr )
        
        self.fading = False
        self.fadetime = 0.0
        self.rotation[0].visible = True
        self.rotation[0].opacity = self.MAXOPACITY   
        self.schedule()
        
    def schedule(self):
        time = random.randint(self.min_t, self.max_t)
        pyglet.clock.schedule_once(self.start_fade, time)
        
    def start_fade(self, t):
        self.rotation.rotate()
        self.rotation[1].opacity = self.MAXOPACITY
        self.rotation[0].opacity = 0
        self.rotation[0].visible = True
        self.fading = True
        
        
    def update(self, dt):
        self.rotation[0].scale += self.ZOOMAMOUNT
        if self.fading:
            self.fadetime += dt
            if self.fadetime >= self.FADEDELAY:
                self.fadetime = 0.0
                old = self.rotation[1]
                new = self.rotation[0]
                delta = dt * self.rate
                old.opacity -= delta
                new.opacity += delta
                if new.opacity >= self.MAXOPACITY:
                    self.fading = False
                    old.visible = False
                    new = self.MAXOPACITY
                    self.schedule()
        
    def draw(self):
        self.batch.draw()