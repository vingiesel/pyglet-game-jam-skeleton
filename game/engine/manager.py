import pyglet, os
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
        self.data = {}
        pyglet.clock.schedule_interval(self.tick, 1 / 60.0)

        
        glEnable(GL_TEXTURE_2D)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glShadeModel(GL_SMOOTH)
        glClearDepth(1.0)
        glEnable(GL_DEPTH_TEST)
        glDepthFunc(GL_LEQUAL)
        glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)
        glEnable(GL_ALPHA_TEST)


    def change_scene(self, scene, context=None):
        self._remove_current_scene()

        scene = scene(manager=self)
        self.stack = [scene]
        scene.start(context)

    def add_scene(self, scene, context=None):
        current_scene = self.stack[0]
        current_scene.pause()

        scene = scene(manager=self)
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


    # data management
    def load_data_bundle(self, name, structure):
        data = {'images': {}, 'sounds': {}}
        for image_name, image_path in structure.get('images', []).items():
            image_path = os.path.join('assets', image_path)
            image = pyglet.image.load(image_path, decoder=pyglet.image.codecs.png.PNGImageDecoder())
            data['images'][image_name] = image

        self.data[name] = data


    def unload_data_bundle(self, name):
        pass

    def run(self):
        pyglet.app.run()


game_window = GameWindow()