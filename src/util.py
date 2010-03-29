import pyglet

def img(filename):
    return pyglet.resource.image(filename)

def spr(filename, **kwargs):
    return pyglet.sprite.Sprite(img(filename), **kwargs)


from math import floor

def gradient(start, end, steps):
    step = {
        'r' : (start[0] - end[0]) / (steps - 1),
        'g' : (start[1] - end[1]) / (steps - 1),
        'b' : (start[2] - end[2]) / (steps - 1),
    }
    
    gradient = []
    for i in  range(steps):
        r = start[0] - (step['r'] * i)
        g = start[1] - (step['g'] * i)
        b = start[2] - (step['b'] * i)
        gradient.append((r,g,b))
    return gradient