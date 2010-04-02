
import os
import os.path

orig_join = os.path.join

def myjoin(*paths):
    joined_path = os.path.normpath(orig_join(*paths))
    if __debug__:
        print joined_path
    return joined_path


os.path.join = myjoin

import gc

import pyglet
from pyglet.window import key
# Import our submodule
import scenes

import pyglet.media

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600


class GameWindow(pyglet.window.Window):
    def __init__(self):
        super(GameWindow, self).__init__(WINDOW_WIDTH, WINDOW_HEIGHT, caption="Wasers")
        self.setup_gl()
        # pyglet.clock.schedule(self.update)
        pyglet.clock.schedule_interval(self.update, 1.0/30.0)
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)
        # cache image resources
        pyglet.resource.path = ['dat', 'dat/img/', 'dat/img/bgd', 'dat/font', 'dat/audio', 'dat/audio/fx']
        pyglet.resource.reindex()
        pyglet.resource.add_font('psychotic.ttf')
        # create background manager
        
        self.music_player = pyglet.media.Player()
        self.music_player.eos_action = pyglet.media.Player.EOS_LOOP
        self.music_player.volume = 0.5
        self.music_player.queue(pyglet.media.load('dat/audio/1indus.mp3'))
        # Create a reference for the current scene
        self.scene = None
        self._game_scene = scenes.GameScene(self)
        
        self.fps_display = pyglet.clock.ClockDisplay()
        # Set initial scene with our utility function
        self.gamescene()

    def setup_gl(self):
        pyglet.gl.glClearColor(0.133, 0.133, 0.133, 1.0)
        pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(pyglet.gl.GL_SRC_ALPHA,
                pyglet.gl.GL_ONE_MINUS_SRC_ALPHA)
  
    def update(self, dt):
        # Here we tell the current scene to update its logic
        self.scene.update(dt)
        gc.collect(2)

    def on_draw(self):
        self.clear()
        # Here we hand off the drawing to the current scene
        self.scene.draw()
        
        if __debug__:
            self.fps_display.draw()
    
    # This utility function will remove the current scene and set a new one
    def _set_scene(self, scene):
        # Pop the current scene's event handers
        self.remove_handlers(self.scene)
        # Set the new scene reference
        self.scene = scene
        # Push the new scene's event handlers
        self.push_handlers(self.scene)
    
    # Utility methods to easily set the two scenes we're using in this example
    def splashscene(self):
        if __debug__: print 'pausing game scenes music'
        self.music_player.pause()
        self._set_scene(scenes.SplashScene(self))
    
    def gamescene(self):
        self._set_scene(self._game_scene)
        
    def scorescene(self, score=0):
        self._set_scene(scenes.ScoreScene(self, score))
        
    def preload_gamescene(self):
        self._game_scene = scenes.GameScene(self)

def run():
    window = GameWindow()
    pyglet.app.run()
