import pickle, random

import pyglet

from src.util import img
from src.blob import Blob

Blob.IDLEWOBBLE = 0.015

class BlobController(object):
    def __init__(self, blob):
        self.ox, self.oy = blob.x, blob.y
        blob.y = -random.randint(20, 600)
        dir = random.randint(50, 300)
        dir = dir if random.randint(0,1) else -dir
        blob.x = self.ox + dir
        if blob.x >= 600:
            blob.x - abs(dir) * 2
        elif blob.x <= 0:
            blob.x + abs(dir) * 2
        
        self.blob = blob
        
        self.vx = 1 if self.ox - blob.x > 0 else -1
        self.vy = 1 if self.oy - blob.y > 0 else -1
        
    def update(self, dt):
        if self.blob.y != self.oy:
            self.blob.y += (100 * dt) * self.vy
            if abs(self.blob.y - self.oy) <= 5:
                self.blob.y = self.oy
        else:
            if self.blob.x != self.ox:
                self.blob.x += (100 * dt) * self.vx
                if abs(self.blob.x - self.ox) <= 5:
                    self.blob.x = self.ox
        

# This scene class is the object that the application class maintains
class SplashScene(object):
    def __init__(self, window):
        # Store a reference to the application window
        self.window = window
        
        self.blob_batch = pyglet.graphics.Batch()
        
        positions = pickle.load(open('dat/splashblobs.pkl'))
        self.blobs = []
        for pos in positions:
           blob_filename = random.choice( ['blob.png', 'blob2.png', 'blob3.png'] )
           newblob = Blob(dots=3, doprints=False, batch=self.blob_batch)
           newblob.IDLEWOBBLE = 0.01
           newblob.set_position(*pos)
           newblobcon = BlobController(newblob)
           self.blobs.append(newblobcon)        

    def on_key_press(self, symbol, modifiers):
        pass
        #=======================================================================
        # positions = []
        # for blob in self.blobs:
        #   positions.append((blob.x, blob.y))
        # pickle.dump(positions, open('dat/splashblobs.pkl', 'w'))
        #=======================================================================
    
    def on_mouse_press(self, x, y, button, modifiers):
        pass
        #------------- newblob = Blob('blob.png', dots=3, batch=self.blob_batch)
        #-------------------------------------------- newblob.set_position(x, y)
        #-------------------------------------------- self.blobs.append(newblob)

    def update(self, dt):
        for blob in self.blobs:
            blob.update(dt)

    def draw(self):
        self.blob_batch.draw()