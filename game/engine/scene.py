class BaseScene:
    def __init__(self, manager):
        self.running = True
        self.manager = manager

    def start(self, context=None):
        pass

    def end(self):
        self.running = False

    def on_unload(self):
        pass

    def on_pause(self):
        pass

    def on_unpause(self):
        pass

    def on_draw(self, window):
        pass

    def on_tick(self, dt):
        pass