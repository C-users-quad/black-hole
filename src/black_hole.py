from settings import *
from utils import get_schwarzschild_radius

class BlackHole:
    def __init__(self, mass):
        self.pos = np.array([[0, 0]], dtype=np.float32)
        self.mass = mass
        self.r_s = get_schwarzschild_radius(self.mass) * 0.0000001
        self.color = np.array([[1.0, 1.0, 1.0]], dtype=np.float32)
