import pyglet

class ScoreLabel(pyglet.text.Label):
    
    floatamount = 30
    fadeamount = 275
    
    def __init__(self, text, x, y, color, size=10, bold=True, batch=None, group=None):
        super(ScoreLabel, self).__init__(text=text, 
            font_name=None, font_size=size, 
            bold=bold, italic=False, 
            color=(list(color) + [255]), 
            x=x, y=y, width=None, height=None, 
            anchor_x='center', anchor_y='baseline', 
            halign='left', multiline=False, 
            batch=batch, group=group)
        self.alpha = 255.0
        self.ocolor = color
        
    def update(self, dt):
        self.y += self.floatamount * dt                
        self.alpha -= self.fadeamount * dt
        self.begin_update()
        self.color = (list(self.ocolor) + [int(self.alpha)])
        self.end_update()
        if self.color[-1] <= 0:
            return True