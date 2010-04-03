import pickle, random, time

import pyglet

import src
from src.util import img
from src.blob import Blobule
import config
from scene import Scene

class SplashImage(pyglet.sprite.Sprite):
    def __init__(self, image, batch, group, x, y, wait1, fadein, wait2, fadeout, maxopacity=255):
        image.anchor_x, image.anchor_y = 300, image.height / 2
        super(SplashImage, self).__init__(image, batch=batch, group=group)
        self.x = x
        self.y = y
        self.opacity = 0
        
        self.wait1 = wait1
        self.wait2 = wait2
        self.fadein = fadein
        self.fadeout = fadeout
        
        self.fade1 = False
        self.fade2 = False
        self.maxopacity = maxopacity
        pyglet.clock.schedule_once(self._start_fade1, self.wait1)
        
    def _start_fade1(self, dt):
        print 'start fade1'
        self.fade1 = True
        
    def _start_fade2(self, dt):
        print 'start fade2'
        self.fade2 = True

    def update(self, dt):
        if self.fade1:
            self.opacity += self.fadein * dt
            if self.opacity >= self.maxopacity:
                self.opacity = self.maxopacity
                self.fade1 = False
                if self.wait2 >= 0.0:
                    pyglet.clock.schedule_once(self._start_fade2, self.wait2)
        elif self.fade2:
            self.opacity -= self.fadeout * dt
            if self.opacity <= 0:
                self.opacity = 0
                self.fade2 = False
                self.visible = False
    def unschedule(self):
        pyglet.clock.unschedule(self._start_fade1)
        pyglet.clock.unschedule(self._start_fade2)

class PlayerController(object):
    def __init__(self, scene, group, x, y, player_dot=False):
        self.group = group
        self.ox, self.oy = x, y
        
        if player_dot:
            self.blobule = Blobule(group, dots=1)
        else:
            self.blobule = Blobule(group, dots=5, accel_max=1.5)
            
    def update(self, dt):
        offset = 100.0 * dt
        offset = min(offset, self.oy - self.group.y)
        self.group.offsetPosition(0.0, offset)
        if self.group.x >= -10:
            self.group.tick()
            
# This scene class is the object that the application class maintains
class SplashScene(Scene):
    def __init__(self, window):
        # Store a reference to the application window
        pyglet.gl.glClearColor(0.133, 0.133, 0.133, 1.0)
        self.window = window
        self.splash_batch = pyglet.graphics.Batch()
        self.label_group = pyglet.graphics.OrderedGroup(1)
        self.bg_group = pyglet.graphics.OrderedGroup(0)
        
        rnd = random.Random(time.time())
        
        self.blobs = []
        self.blob_groups = []
        
        self.player_blob_group = src.glsl.blob.BlobGroup(300, -800, 8, (0.125, 0.375, 0.0))
        self.player_blob = PlayerController(self, self.player_blob_group, 300, 300, True)
        self.blobs.append(self.player_blob)
        
        self.done = False
        
        self.splash_images = []
        splashbg = SplashImage(img('splashbg.png'),
              self.splash_batch, self.bg_group,
              300, 300,
              0, 60,
              5, 90
              )
        self.splash_images.append(splashbg)
        
        splasha = SplashImage(img('splash_a.png'),
              self.splash_batch, self.label_group,
              300, 388,
              2, 230,
              2, 170
              )
        self.splash_images.append(splasha)
        
        splashname = SplashImage(img('splash_pyweeklings.png'),
              self.splash_batch, self.label_group,
              300, 300,
              3, 120,
              4, 170
              )
        self.splash_images.append(splashname)
        
        splashgame = SplashImage(img('splash_game.png'),
              self.splash_batch, self.label_group,
              300, 221,
              4, 230,
              2, 170
              )
        self.splash_images.append(splashgame)
        
        babaroa = SplashImage(img('dempa.png'),
              self.splash_batch, self.bg_group,
              300, 300,
              9, 80,
              -1, 0,
              maxopacity=128,
              )
        self.splash_images.append(babaroa)
        
        self.logo = SplashImage(img('logo.png'),
              self.splash_batch, self.label_group,
              300, 300,
              9, 80,
              -1, 90
              )
        self.splash_images.append(self.logo)
        
        multipliers = [0.0, 0.3, 0.8]
        
        for i in xrange(7):
            for j in xrange(8):
                r = b = random.choice(multipliers[:-1])
                g = min(1.0, r + random.choice(multipliers[1:]))
                column = rnd.randint(10, 590)
                blob_group = src.glsl.blob.BlobGroup(
                 column, rnd.randint(-100 * (j + 1), -100 * j),
                 8, (r, g, b)
                )
                self.blob_groups.append(blob_group)
                newblob = PlayerController(self, blob_group, column, 610)
                self.blobs.append(newblob)
                
        self.doblobs = False
        pyglet.clock.schedule_once(self._set_do_blobs, 4.0)
        
        if config.options['USE_SOUND']:
            self.intro_player = pyglet.media.Player()
            self.intro_sound = pyglet.media.load('dat/audio/1creepy.mp3', streaming=False)
            self.intro_player.queue(self.intro_sound)
            self.intro_player.volume = 0.1
            self.intro_player.play()
    
    def enter(self):
        if config.options['USE_SOUND']:
            self.window.music_player.pause()
    
    def leave(self):
        if config.options['USE_SOUND']:
            self.intro_player.pause()
    
    def _set_do_blobs(self, dt):
        self.doblobs = True

    def on_key_press(self, symbol, modifiers):
        if symbol == pyglet.window.key.ESCAPE :
            self.change_to_game_scene()
        return True
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

    def change_to_game_scene(self):
        pyglet.clock.unschedule(self._set_do_blobs)
        for img in self.splash_images:
            img.unschedule()
        self.window.gamescene()
        
        
    def update(self, dt):
        if __debug__: print self.logo.opacity
        for image in self.splash_images:
            image.update(dt)
            
        if self.doblobs:
            dead_blobs = []
            for blob in self.blobs:
                blob.update(dt)
                if not blob is self.player_blob and blob.oy == blob.group.y:
                    dead_blobs.append(blob)
                    
            for blob in dead_blobs:
                self.blobs.remove(blob)
                self.blob_groups.remove(blob.group)
                
        if self.player_blob_group.y == 300 and not self.blob_groups and not self.done:
            self.done = True
            self.change_to_game_scene()
            
    def do_gamescene(self, dt):
        del self.newblob_group
        del self.blob_groups
        del self.blobs
        self.window.gamescene() 

    def draw(self):
        if __debug__: print self.logo.opacity
        self.splash_batch.draw()
        if self.doblobs:
            for group in [self.player_blob_group] + self.blob_groups:
                if group.y >= -10:
                    group.draw(600, 600)
                    
