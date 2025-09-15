from vispy import app, gloo
import numpy as np
from numba import njit

# window stuff
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
DT = 0.01

# physical constants
G = 6.674e-11 # gravitational constant
c = 3e8 # speed of light
sol = 1.989e30 # solar mass

# camera stuff
MIN_SPEED, MAX_SPEED = 100.0, 5000.0
MIN_ZOOM = 1e-5
MOVEMENT_KEYS = ['W', 'A', 'S', 'D']

