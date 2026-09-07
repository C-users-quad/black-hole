from settings import *
from utils import *

class Camera:
    """An arcball camera"""
    def __init__(self, pos, target):
        # store camera position and position the camera orbits/looks at
        self.pos = np.array(pos)
        self.old_pos = self.pos.copy()
        self.target = np.array(target)

        # calculate angles
        offset = self.pos - self.target
        self.radius = np.linalg.norm(offset)
        self.elevation = np.asin(offset[1] / self.radius)
        self.azimuth = np.atan2(offset[0], offset[2])

    def update(self, input, dt):
        self.parse_input(input, dt)
        self.update_pos()

    def parse_input(self, input, dt):
        for key in input:
            if key == "W":
                self.update_elevation(-1, dt)
            elif key == "A":
                self.update_azimuth(-1, dt)
            elif key == "S":
                self.update_elevation(1, dt)
            elif key == "D":
                self.update_azimuth(1, dt)

    def update_elevation(self, move_dir, dt):
        new_elevation = self.elevation + move_dir * PAN_SPEED * dt
        self.elevation = self.elevation * 0.9 + new_elevation * 0.1
        # prevents camera flipping over the poles
        self.elevation = clamp(
            self.elevation, -np.pi/2 + np.pi/16, np.pi/2 - np.pi/16
        )

    def update_azimuth(self, move_dir, dt):
        new_azimuth = self.azimuth + move_dir * PAN_SPEED * dt
        self.azimuth = self.azimuth * 0.9 + new_azimuth * 0.1

    def update_zoom(self, scroll_dir, dt):
        self.radius += scroll_dir * ZOOM_SPEED * dt
        self.radius = clamp(self.radius, MIN_ZOOM, MAX_ZOOM)

    def update_pos(self):
        self.old_pos = self.pos.copy()
        self.pos[0] = (
            self.target[0] + self.radius
            * np.cos(self.elevation) * np.sin(self.azimuth)
        )
        self.pos[1] = (
            self.target[1] + self.radius
            * np.sin(self.elevation)
        )
        self.pos[2] = (
            self.target[2] + self.radius
            * np.cos(self.elevation) * np.cos(self.azimuth)
        )

    def get_pos(self):
        return self.pos.tolist()

    def moved(self):
        return self.old_pos != self.pos
