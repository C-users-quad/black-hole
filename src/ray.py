from settings import *
from utils import *

class Ray:
    def __init__(self, pos, vel, bh_mass, r_s):
        self.pos = np.array(pos)
        self.r, self.theta, self.phi = (
            cartesian_to_spherical_pos(pos)
        )
        self.dr, self.dtheta, self.dphi = (
            cartesian_to_spherical_vel(vel, pos)
        )
        self.E = compute_E(bh_mass, self.r, self.dr, self.dphi)
        # when reconstructing dt use compute_dt()
