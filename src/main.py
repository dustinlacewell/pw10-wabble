import pyglet
from pyglet.window import key
# Import our submodule
import scenes

pyglet.options['debug'] = False

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600


class GameWindow(pyglet.window.Window):
    def __init__(self):
        super(GameWindow, self).__init__(WINDOW_WIDTH, WINDOW_HEIGHT, caption="Wasers")
        self.setup_gl()
        pyglet.clock.schedule(self.update)
        self.keys = pyglet.window.key.KeyStateHandler()
        self.push_handlers(self.keys)
        # cache image resources
        pyglet.resource.path = ['dat/img/', 'dat/img/bgd']
        pyglet.resource.reindex()
        # create background manager
        # Create a reference for the current scene
        self.scene = None
        
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

    def on_draw(self):
        self.clear()
        # Here we hand off the drawing to the current scene
        self.scene.draw()
        
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
        self._set_scene(scenes.SplashScene(self))
    
    def gamescene(self):
        self._set_scene(scenes.GameScene(self))

def run():
    window = GameWindow()
    pyglet.app.run()
