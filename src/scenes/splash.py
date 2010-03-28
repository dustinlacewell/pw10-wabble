import pickle, random

import pyglet

from src.util import img
from src.blob import Blob

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
           newblob = Blob(dots=3, batch=self.blob_batch, footprints=False)
           newblob.set_position(*pos)
           self.blobs.append(newblob)
        self.blobs = []
        

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
        pass

    def draw(self):
        self.blob_batch.draw()