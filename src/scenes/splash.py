import pickle, random

import pyglet

import src
from src.util import img
from src.blob import Blob
from src.player import Player

Blob.IDLEWOBBLE = 0.015

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

class PlayerController(object):
    def __init__(self, scene, group, x, y):
        self.ox, self.oy = x, y
        ry = -random.randint(100, 500)
        dir = random.randint(50, 300)
        dir = dir if random.randint(0,1) else -dir
        rx = self.ox + dir
        if rx >= 600:
            rx - abs(dir) * 2
        elif rx <= 0:
            rx + abs(dir) * 2
            
        self.dottime = 0.0
        self.rndx = []
        self.rndy = []
        for x in range(4):
            rndx = random.randint(1, 4)
            rndx = rndx if random.randint(0,1) else -rndx
            rndy = random.randint(1, 4)
            rndy = rndy if random.randint(0,1) else -rndy
            self.rndx.append(rndx)
            self.rndy.append(rndy)
        
        self.player = Player(scene, group, rx, ry)
        
        self.vx = 1 if self.ox - self.player.x > 0 else -1
        self.vy = 1 if self.oy - self.player.y > 0 else -1
        
        pyglet.clock.schedule_interval(self.wobble, .05)
        
    def wobble(self, dt):
        for dot in self.player.dots:
            dot.setRoot(self.player.x, self.player.y)
            dot.x = self.player.x + random.choice(self.rndx)
            dot.y = self.player.y + random.choice(self.rndy)
        
    def update(self, dt):
        blob = self.player.blob
        
        dx, dy = self.player.x, self.player.y
        if self.player.y != self.oy:
            self.player.y += (100 * dt) * self.vy
            if abs(self.player.y - self.oy) <= 5:
                self.player.y = self.oy
        else:
            if self.player.x != self.ox:
                self.player.x += (100 * dt) * self.vx
                if abs(self.player.x - self.ox) <= 5:
                    self.player.x = self.ox
        location = (self.player.x, self.player.y)
        offset_x = dx - self.player.x
        offset_y = dy - self.player.y
        
    def die(self):
        pyglet.clock.unschedule(self.wobble)
        

# This scene class is the object that the application class maintains
class SplashScene(object):
    def __init__(self, window):
        # Store a reference to the application window
        self.window = window
        self.splash_batch = pyglet.graphics.Batch()
        self.label_group = pyglet.graphics.OrderedGroup(1)
        self.bg_group = pyglet.graphics.OrderedGroup(0)
        
        self.blob_group = src.glsl.blob.BlobGroup()
        
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
        
        babaroa = SplashImage(img('babaroa.png'),
              self.splash_batch, self.bg_group,
              300, 300,
              9, 80,
              -1, 0,
              maxopacity=128,
              )
        self.splash_images.append(babaroa)
        
        positions = pickle.load(open('dat/splashblobs.pkl'))
        self.blobs = []
        for pos in positions:
           newblob = PlayerController(self, self.blob_group, pos[0], pos[1])
           self.blobs.append(newblob)    
           
        newblob = PlayerController(self, self.blob_group, 300, 300)
        newblob.player.x = 300
        newblob.player.y = -1500
        self.blobs.append(newblob)
           
        self.doblobs = False
        pyglet.clock.schedule_once(self._set_do_blobs, 4.0)
        
    def _set_do_blobs(self, dt):
        self.doblobs = True

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
        
        for image in self.splash_images:
            image.update(dt)
        if self.doblobs:
            for blob in self.blobs:
                blob.update(dt)
            #self.blob_group.tick()
        if self.blobs[-1].player.y == 300 and not self.done:
            self.done = True
            pyglet.clock.schedule_once(self.do_gamescene, 2)
            
    def do_gamescene(self, dt):
        for b in list(self.blobs[:-1]):
                b.die()
                self.blobs.remove(b)
                self.blob_group.blobs = []
        self.window.gamescene() 

    def draw(self):
        self.splash_batch.draw()
        if self.doblobs:
            self.blob_group.draw(600, 600)