import random

import pyglet

from src.util import spr

class BackgroundManager(object):
    def __init__(self, rotation='backgrounds.txt', min_t=60, max_t=120, rate=50):
        self.min_t = min_t
        self.max_t = max_t    
        self.rate = rate # fade rate    
        
        self.rotation = []
        for line in pyglet.resource.file(rotation):
            self.rotation.append( line.strip() )
            
        self.current = spr(self.rotation[0])
        self.next = None
    
        self.schedule()
        
    def schedule(self):
        time = random.randint(self.min_t, self.max_t)
        pyglet.clock.schedule_once(self.start_fade, time)
        
    def start_fade(self, t):
        self.rotation.append(self.rotation.pop(0))
        self.next = spr(self.rotation[0])
        self.next.opacity = 0
        self.schedule()
        
    def update(self, dt):
        if self.next:
            self.current.opacity -= dt * self.rate
            self.next.opacity += dt * self.rate
            if self.next.opacity >= 255:
                self.current = self.next
                self.next = None
                
    def draw(self):
        self.current.draw()
        if self.next:
            self.next.draw()
    
        