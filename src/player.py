import random

import pyglet

from src.util import spr

class Blob(pyglet.sprite.Sprite):
    def __init__(self, sprite, off_min=2, off_max=6):
        self.off_min = off_min
        self.off_max = off_max
        
    def set_offset(self):
        self.xoff = rand.randint(self.off_min, self.off_max)
        self.yoff = rand.randint(self.off_min, self.off_max)
        
    def update(self, t):
        self.set_offset()
        
        