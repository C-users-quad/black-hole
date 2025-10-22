from settings import *
from utils import *

class Ray:
    def __init__(self, pos, vel, bh_mass):
        self.pos = np.array(pos)
        self.r, self.theta, self.phi = (
            cartesian_to_spherical_pos(pos)
        )
        self.dr, self.dtheta, self.dphi = (
            cartesian_to_spherical_vel(vel, pos)
        )
        self.E = compute_E(bh_mass, self.r, self.dr, self.dphi)
        self.state = np.array([
            self.r,  self.theta,  self.phi,
            self.dr, self.dtheta, self.dphi
        ])

def generate_rays(width, height, cam_pos, bh_mass):
    rays = []
    aspect = width / height
    forward = normalize(-cam_pos)
    right = normalize(np.cross(forward, UP))
    up = np.cross(right, forward)

    for i in range(width):
        for j in range(height):
            x = (
                (2*(i+0.5)/width - 1) *
                (np.tan(np.radians(FOV)/2)*aspect)
            )
            y = (
                (1 - 2*(j+0.5)/height) *
                np.tan(np.radians(FOV)/2)
            )
            dir_ray = normalize(x*right + y*up + forward)
            rays.append(Ray(cam_pos, dir_ray, bh_mass))

    return rays
