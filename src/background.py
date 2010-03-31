import random
from collections import deque

import pyglet

from src.util import spr

class BackgroundManager(object):
    
    # Fade Effect
    MAXOPACITY = 128
    
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
        self.init_fade()
        
        self.__do_zoom = False
        self.init_zoom()
        
        self.__do_spin = False
        self.init_spin()
        
    def _get_visible(self):
        return [bg for bg in self.rotation if bg.visible]
    visible = property(_get_visible)
    
    def init_spin(self,
                  min_st=4, max_st=6,
                  min_spin=15.0, max_spin=180.0,
                  min_amount=3.0, max_amount=12.0):
        self.min_st = min_st
        self.max_st = max_st
        self.min_spin = min_spin
        self.max_spin = max_spin
        self.min_amount = min_amount
        self.max_amount = max_amount
        self.spinning = False
        self.sdirection = 1
        self.spinamount = random.random() * max_spin + min_spin
        self.spindelta = random.random() * max_amount + min_amount
        self.__do_spin = False
        
    def _schedule_spin(self):
        time = random.randint(self.min_st, self.max_st)
        pyglet.clock.schedule_once(self.start_spin, time)
        
    def _get_do_spin(self):
        return self.__do_spin
    def _set_do_spin(self, bool):
        if bool:
            if self.__do_spin:
                return
            self.init_spin()
            self.__do_spin = True
            self._schedule_spin()
        else:
            if not self.__do_spin:
                return
            pyglet.clock.unschedule(self.start_spin)
    do_spin = property(_get_do_spin, _set_do_spin)
            
    def start_spin(self, dt):
        self.spinamount = random.random() * self.max_spin + self.min_spin
        self.spindelta = random.random() * self.max_amount + self.min_amount
        self.sdirection = -self.sdirection
        self.spinning = True  
    
    def init_zoom(self, 
                  min_zt=1, max_zt=2,
                  max_zoom=2.0, min_zoom=1.0, 
                  zoomamount=0.1):
        # Fade Effect Attributes
        self.min_zt = min_zt
        self.max_zt = max_zt
        self.max_zoom = max_zoom
        self.min_zoom = min_zoom
        self.zoomamount = zoomamount
        self.zooming = False
        self.zdirection = 1
        self.__do_zoom = False
        
    def _schedule_zoom(self):
        time = random.randint(self.min_zt, self.max_zt)
        pyglet.clock.schedule_once(self.start_zoom, time)
        
    def _get_do_zoom(self):
        return self.__do_zoom
    def _set_do_zoom(self, bool):
        if bool:
            if self.__do_zoom:
                return
            self.init_zoom()
            self.__do_zoom = True
            self._schedule_zoom()
        else:
            if not self.__do_zoom:
                return
            pyglet.clock.unschedule(self.start_zoom)
    do_zoom = property(_get_do_zoom, _set_do_zoom)
            
    def start_zoom(self, dt):
        if self.rotation[1].scale == self.max_zoom:
            self.zdirection = -1
        else:
            self.zdirection = 1
        self.zooming = True   
               
        
    def init_fade(self, min_ft=8, max_ft=9, fadeamount=20):
        # Fade Effect Attributes
        self.min_ft = min_ft # minimum time between fades
        self.max_ft = max_ft # maximum time between fades    
        self.fadeamount = fadeamount # opacity per tick
        self.fading = False # actually fading
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
        self.rotation[0].scale = 1
        self.rotation[0].visible = True
        self.fading = True
        
        
    def update(self, dt):
        # Fade effect
        if self.fading:
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
                self.zooming = False
                self.spinning = False
                if random.random() > 0.20:
                    if self.do_zoom:
                        self._schedule_zoom()
                    if self.do_spin:
                        self._schedule_spin()
                            
        bgimg = self.rotation[1]
                            
        # Zoom effect
        if self.zooming:
            bgimg.scale += ((bgimg.scale * self.zoomamount) * dt) * self.zdirection
            bgimg.scale = min(self.max_zoom, max(self.min_zoom, bgimg.scale))
            if bgimg.scale <= self.min_zoom or bgimg.scale >= self.max_zoom:
                self.zooming = False
                self._schedule_zoom()
                    
        if self.spinning:
            amount = self.spindelta * dt
            self.spinamount -= amount
            bgimg.rotation += amount * self.sdirection
            if self.spinamount <= 0:
                self.spinning = False
                self._schedule_spin()
                    
    def draw(self):
        self.batch.draw()