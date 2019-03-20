import pyglet
from pyglet.gl import *

# import UserList, UserString, commands

print('running')

window = pyglet.window.Window()

background = pyglet.resource.image('assets/back.png')
circle = pyglet.resource.image('assets/circle.png')


@window.event
def on_draw():
    window.clear()
    glEnable(GL_BLEND)

    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    background.blit(0, 0)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    circle.blit(10, 0)

pyglet.app.run()

