import random
from collections import deque

import pyglet

from src.util import spr

class BackgroundManager(object):
    
    # Fade Effect
    MAXOPACITY = 145
    
    def __init__(self, rotation='backgrounds.txt', batch=None, group=None):
        self.batch = batch
        self.group = group         
        
        self.rotation = deque()
        for line in pyglet.resource.file(rotation):
            newspr = spr(line.strip(), batch=batch, group=group)
            newspr.image.anchor_x, newspr.image.anchor_y = 300, 300
            newspr.x, newspr.y = 300, 300
            newspr.visible = False
            newspr.opacity = self.MAXOPACITY
            self.rotation.append(newspr)
        self.rotation[0].visible = True
        
        self.__do_fade = False
        self.do_fade = True   
        
    def _get_visible(self):
        return [bg for bg in self.rotation if bg.visible]
    visible = property(_get_visible)  
        
    def init_fade(self, min_ft=8, max_ft=9, faderate=0.05, fadeamount=20):
        # Fade Effect Attributes
        self.min_ft = min_ft # minimum time between fades
        self.max_ft = max_ft # maximum time between fades    
        self.faderate = faderate # delay between ticks
        self.fadeamount = fadeamount # opacity per tick
        self.fading = False # actually fading
        self.fadetime = 0.0 # fade timer
        self.__do_fade = False
    
    def _schedule_fade(self):
        time = random.randint(self.min_ft, self.max_ft)
        pyglet.clock.schedule_once(self.start_fade, time)
        
    def _get_do_fade(self):
        return self.__do_fade
    def _set_do_fade(self, bool):
        if bool:
            if self.__do_fade:
                return
            self.init_fade()
            self.__do_fade = True
            self._schedule_fade()
        else:
            if not self.__do_fade:       
                return
            pyglet.clock.unschedule(self.start_fade)
    do_fade = property(_get_do_fade, _set_do_fade)
    
    def start_fade(self, t):
        self.rotation.rotate()
        self.rotation[1].opacity = self.MAXOPACITY
        self.rotation[0].opacity = 0
        self.rotation[0].visible = True
        self.fading = True
        
        
    def update(self, dt):
        # Fade effect
        if self.fading:
            self.fadetime += dt
            if self.fadetime >= self.faderate:
                self.fadetime = 0.0
                old = self.rotation[1]
                new = self.rotation[0]
                delta = dt * self.fadeamount
                old.opacity -= delta
                new.opacity += delta
                if new.opacity >= self.MAXOPACITY:
                    self.fading = False
                    old.visible = False
                    new = self.MAXOPACITY
                    self._schedule_fade()
        
    def draw(self):
        self.batch.draw()