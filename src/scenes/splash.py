import pickle, random

import pyglet

from src.util import img
from src.blob import Blob

Blob.IDLEWOBBLE = 0.015

class SplashImage(pyglet.sprite.Sprite):
    def __init__(self, image, batch, group, x, y, wait1, fadein, wait2, fadeout):
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
            if self.opacity >= 255:
                self.opacity = 255
                self.fade1 = False
                if self.wait2 >= 0.0:
                    pyglet.clock.schedule_once(self._start_fade2, self.wait2)
        elif self.fade2:
            self.opacity -= self.fadeout * dt
            if self.opacity <= 0:
                self.opacity = 0
                self.fade2 = False
                self.visible = False

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
        self.splash_batch = pyglet.graphics.Batch()
        self.label_group = pyglet.graphics.OrderedGroup(1)
        self.bg_group = pyglet.graphics.OrderedGroup(0)
        
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
              -1, 0
              )
        self.splash_images.append(babaroa)
        
        positions = pickle.load(open('dat/splashblobs.pkl'))
        self.blobs = []
        for pos in positions:
           blob_filename = random.choice( ['blob.png', 'blob2.png', 'blob3.png'] )
           prints = 0 if random.random() > 0.2 else 6
           newblob = Blob(dots=3, prints=prints, batch=self.blob_batch)
           newblob.IDLEWOBBLE = 0.01
           newblob.set_position(*pos)
           newblobcon = BlobController(newblob)
           self.blobs.append(newblobcon)    
           
        newblob = Blob(dots=3, batch=self.blob_batch)
        newblob.x = newblob.y = 300
        blobcon = BlobController(newblob) 
        blobcon.blob.x = 300
        blobcon.blob.y = -1000
        self.blobs.append(blobcon)
           
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
        if self.blobs[-1].blob.y == 300:
            for blob in self.blobs[:-1]:
                blob.blob.opacity -= 80 * dt
                if blob.blob.opacity <= 0:
                    blob.blob.opacity = 0
                for dot in blob.blob.dots:
                    dot.opacity -= 80 * dt
                    if dot.opacity <= 0:
                        dot.opacity = 0
        if self.blobs[0].blob.opacity == 0:
            self.window.gamescene()

    def draw(self):
        self.splash_batch.draw()
        if self.doblobs:
            self.blob_batch.draw()