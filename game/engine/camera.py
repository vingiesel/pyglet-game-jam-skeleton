from pyglet.gl import glTranslatef

class Mutate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __enter__(self):
        glTranslatef(-self.x, -self.y, 0)
    def __exit__(self, type, value, tb):
        glTranslatef(self.x, self.y, 0)

class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0
        self.zoom = 1

        self.width = width
        self.height = height

        self.rotation = 0

        self.target_x = 0
        self.target_y = 0

        self.max_speed = 0

    def on_update(self, dt):
        mxs = self.max_speed * dt
        self.x = self.x - max(min(self.x - (self.target_x or self.x), mxs), -mxs)
        self.y = self.y - max(min(self.y - (self.target_y or self.y), mxs), -mxs)

    def move_to(self, x, y):
        self.x = self.target_x = x
        self.y = self.target_y = y
        self.max_speed = 0

    def look_at(self, x, y, max_speed=0):
        self.target_x = x
        self.target_y = y
        self.max_speed = max_speed

    def mutate(self):
        return Mutate(self.x, self.y)

    
