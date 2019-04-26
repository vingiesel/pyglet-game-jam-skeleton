from game.engine.scene import BaseScene
from game.engine.camera import Camera
from game.engine.config import config


import pyglet, math


class Game(BaseScene):
    def start(self, context=None):
        self.manager.load_data_bundle('default', {
            'images': {
                'back':'back.png',
                'circle':'circle.png',
                'mist': 'mist.png',
            }
        })

        self.batch = pyglet.graphics.Batch()

        self.background = pyglet.graphics.OrderedGroup(0)
        self.midground = pyglet.graphics.OrderedGroup(1)
        self.foreground = pyglet.graphics.OrderedGroup(2)

        self.sprites = [
            pyglet.sprite.Sprite(self.manager.data['default']['images']['back'], x=0, y=0, batch=self.batch, group=self.background),
            pyglet.sprite.Sprite(self.manager.data['default']['images']['circle'], x=10, y=10, batch=self.batch, group=self.midground),
            pyglet.sprite.Sprite(self.manager.data['default']['images']['mist'], x=200, y=100, batch=self.batch, group=self.foreground)
        ]

        self.camera = Camera(config.res_x, config.res_y)

        # self.camera.look_at(10, 0, 1)

        self.ticks = 0

    def on_tick(self, dt):
        self.camera.on_update(dt)

        self.ticks += dt

        back, circle, mist = self.sprites

        circle.x = (math.sin(10 * self.ticks + 10) * 150) + 150
        mist.scale = (math.sin(10*self.ticks) / 2) + 1

    def on_draw(self, window):
        # self.manager.data['default']['images']['back.png'].blit(0,0)

        with self.camera.mutate():
            self.batch.draw()