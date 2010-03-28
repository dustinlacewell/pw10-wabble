import pyglet
from pyglet.window.key import *

from src.blob import Blob


#class Player(pyglet.sprite):
class Player(Blob):
    
    speed = 2
    radius = 10

    def __init__(self, scene, batch=None, group=None, pgroup=None):
        super(Player, self).__init__(dots=10, batch=batch, group=group, pgroup=pgroup)
        self.scene = scene
        self.x = self.y = 300
        
    def handle_movement(self, dt):
        
        k = self.scene.keys
        old = self.position

        self.y += self.speed if k[UP] else -self.speed if k[DOWN] else 0
        self.x += self.speed if k[RIGHT] else -self.speed if k[LEFT] else 0
        
        if old != self.position:
            self.wobble(dt)
        
    def update(self, dt):
        self.handle_movement(dt)