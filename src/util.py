import pyglet

def img(filename):
    return pyglet.resource.image(filename)

def spr(filename):
    return pyglet.sprite.Sprite(img(filename))