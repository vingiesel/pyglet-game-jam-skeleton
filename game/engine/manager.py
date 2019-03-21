import pyglet
from pyglet.gl import *

from game import scenes

from game.engine.config import config


class GameWindow(pyglet.window.Window):
    def __init__(self):
        super(GameWindow, self).__init__(
            config.res_x,
            config.res_y,
            caption='Game',
            resizable=False)
        self.stack = []
        pyglet.clock.schedule_interval(self.tick, 1 / 60.0)

    def change_scene(self, scene, context=None):
        self._remove_current_scene()

        scene = scene()
        self.stack = [scene]
        scene.start(context)

    def add_scene(self, scene, context=None):
        current_scene = self.stack[0]
        current_scene.pause()

        scene = scene()
        self.stack.append(scene)
        scene.start(context)

    def _remove_current_scene(self):
        if self.stack:
            current_scene = self.stack.pop(0)
            current_scene.on_unload()

        if self.stack:
            self.stack[0].un_pause()
    

    # window events
    def on_draw(self):
        self.clear()
        # draw depth first
        for scene in self.stack:
            scene.on_draw(self)

    def tick(self, dt):
        for scene in self.stack[:1]:
            scene.on_tick(dt)

        if not scene.running:
            self._remove_current_scene()
                
        if not self.stack:
            pyglet.app.exit()

    def run(self):
        pyglet.app.run()


game_window = GameWindow()