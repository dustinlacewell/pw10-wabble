import pyglet

from src.util import img
from src.blob import Blob

# This scene class is the object that the application class maintains
class GameScene(object):
    def __init__(self, window):
        # Store a reference to the application window
        self.window = window
        self.blob = Blob('blob.png')
        self.blob.set_position(300, 300)

    def on_key_press(self, symbol, modifiers):
        pass

    def update(self, dt):
        pass

    def draw(self):
        self.blob.draw()