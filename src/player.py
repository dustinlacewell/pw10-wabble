import pyglet
from pyglet.window.key import *

from src.blob import Blob


class Player(Blob):

    radius = 10

    def __init__(self, scene, batch=None, group=None, pgroup=None):
        super(Player, self).__init__(dots=5, doprints=True, batch=batch, group=group, pgroup=pgroup)
        self.scene = scene
        self.speed = self.MAXSPEED
        
    def handle_movement(self, dt):
        k = self.scene.keys
        old = self.position
        rawspeed = self.MAXSPEED - ((len(self.dots) - 5) * 10)
        speed = max(self.MINSPEED, rawspeed) * dt
        self.y += speed if k[UP] else -speed if k[DOWN] else 0
        self.x += speed if k[RIGHT] else -speed if k[LEFT] else 0
        
        if old != self.position:
            self.wobble(dt)
        
    def update(self, dt):
        self.handle_movement(dt)
        
    def remove_dot(self):
        super(Player, self).remove_dot()
        super(Player, self).remove_dot()
        super(Player, self).remove_dot()
        if len(self.dots) <= 5:
            return True