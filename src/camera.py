from settings import *

class Camera:
    def __init__(self):
        self.pos = np.array([WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2], dtype=np.float32)
        self.speed = 100
        self.zoom = 1.0

    def update_speed(self, event_y):
        self.speed *= 1.1**event_y
        self.speed = min(MAX_SPEED, max(self.speed, MIN_SPEED))

    def update_zoom(self, event_y):
        self.zoom *= 1.1**event_y
        self.zoom = max(MIN_ZOOM, self.zoom)

    def update_pos(self, key, dt):
        if key == 'W':
            self.pos[1] -= self.speed * dt
        elif key == 'A':
            self.pos[0] -= self.speed * dt
        elif key == 'S':
            self.pos[1] += self.speed * dt
        elif key == 'D':
            self.pos[0] += self.speed * dt

    def update(self, keys, dt):
        for key in keys:
            self.update_pos(key, dt)