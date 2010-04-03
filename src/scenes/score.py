import pickle, random, time

import pyglet

import src
from src.util import img
from src.blob import Blobule
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
        
        self.fade1 = True
        self.fade2 = False
        self.maxopacity = maxopacity
        #pyglet.clock.schedule_once(self._start_fade1, self.wait1)
        
    def _start_fade1(self, dt):
        self.fade1 = True
        
    def _start_fade2(self, dt):
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
            
# This scene class is the object that the application class maintains
class ScoreScene(Scene):
    def __init__(self, window, playerscore):
        window.preload_gamescene()
        pyglet.gl.glClearColor(1.0, 1.0, 1.0, 1.0)
        # Store a reference to the application window
        self.window = window
        self.splash_batch = pyglet.graphics.Batch()
        self.label_group = pyglet.graphics.OrderedGroup(1)
        self.bg_group = pyglet.graphics.OrderedGroup(0)
        
        self.done = False
        
        self.splash_images = []
        scorebg = SplashImage(img('score.png'),
              self.splash_batch, self.bg_group,
              300, 300,
              0, 320,
              -1, 90
              )
        self.splash_images.append(scorebg)

        scoretext = SplashImage(img('scoretext.png'),
              self.splash_batch, self.label_group,
              300, 450,
              0, 320,
              -1, 90
              )
        self.splash_images.append(scoretext)
        
        self.score_labels = []
        self.playerscore = playerscore
        self.lastscore = 0
        self.lastscore_label = pyglet.text.Label('0',
              font_name='Psychotic', font_size=62,
              anchor_x = 'center', anchor_y = 'center',
              batch=self.splash_batch, group=self.label_group,
              x = 300, y=425
              )
        
        highscore_file = pyglet.resource.file('highscores.pkl', mode='r')
        self.highscores = pickle.load(highscore_file)
        self.highscores.append(playerscore)
        self.highscores.sort()
        self.highscores = self.highscores[1:]
        self.highscore_labels = self._get_highscore_labels()
        highscore_file = pyglet.resource.file('highscores.pkl', mode='w')
        pickle.dump(self.highscores, highscore_file)
        
        self.score_done = False
        self.score_labels.append(self.lastscore_label)
        
    def _get_highscore_labels(self):
        highscore_labels = []
        for idx, score in enumerate(self.highscores):
            color = (255, 255, 255, 255)                
            newlabel = pyglet.text.Label(str(score),
            font_name='Psychotic', font_size=48,
            anchor_x = 'center', anchor_y = 'center',
            batch=self.splash_batch, group=self.label_group,
            x = 300, y= 40 + (63 * idx),
            color = color
            )
            highscore_labels.append(newlabel)
        return highscore_labels
        
    def _increase_scorelabel(self, dt):
        self.lastscore += 1
        self.lastscore_label.text = str(self.lastscore)
        if self.lastscore == self.playerscore:
            pyglet.clock.unschedule(self._increase_scorelabel)
            for idx, score in enumerate(self.highscores):
                if score == self.playerscore:
                    if (idx != len(self.highscores) - 1 and self.highscores[idx+1] != score) or idx == len(self.highscores) - 1:
                        label = self.highscore_labels[idx]
                        label.begin_update()
                        self.highscore_labels[idx].color = (0, 255, 0, 255)
                        label.end_update()
                        break
        
        
    def on_key_press(self, symbol, modifiers):
        if self.lastscore == self.playerscore:
            pyglet.clock.unschedule(self._increase_scorelabel)
            self.window.splashscene()

    def update(self, dt):
        for image in self.splash_images:
            image.update(dt)
        for label in self.score_labels:
            label.opacity = self.splash_images[0].opacity
            
        if self.splash_images[0].opacity >= self.splash_images[0].maxopacity and not self.score_done:
            self.score_done = True
            pyglet.clock.schedule_interval(self._increase_scorelabel, 0.05)

    def draw(self):
        self.splash_batch.draw()

